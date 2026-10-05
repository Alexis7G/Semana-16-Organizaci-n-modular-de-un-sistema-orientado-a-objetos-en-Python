import hashlib
import re
from datetime import datetime

from modelos.producto import Producto
from modelos.usuario import Usuario
from modelos.venta import Venta
from servicios.archivo_servicio import ArchivoServicio

ADMIN = "Administrador"
EMPLEADO = "Empleado"
CLIENTE = "Cliente"


class RestauranteServicio:
    """Toda la lógica de negocio, validaciones y persistencia.
    La interfaz solo captura eventos y delega aquí."""

    ROLES_GESTIONABLES = (EMPLEADO, CLIENTE)
    F_USUARIOS = "usuarios.json"
    F_PRODUCTOS = "productos.json"
    F_VENTAS = "ventas.json"

    def __init__(self, archivos=None):
        self.archivos = archivos or ArchivoServicio()
        self.usuarios = [Usuario.from_dict(d) for d in self.archivos.leer(self.F_USUARIOS)]
        self.productos = [Producto.from_dict(d) for d in self.archivos.leer(self.F_PRODUCTOS)]
        self.ventas = [Venta.from_dict(d) for d in self.archivos.leer(self.F_VENTAS)]
        self._datos_iniciales()

    # ---------- utilidades ----------
    @staticmethod
    def _hash(clave):
        return hashlib.sha256(clave.encode("utf-8")).hexdigest()

    @staticmethod
    def _siguiente_id(lista):
        return max((x.id for x in lista), default=0) + 1

    def _datos_iniciales(self):
        if not self.usuarios:
            self.usuarios.append(Usuario(1, "Administrador", "admin@restaurante.com",
                                         ADMIN, self._hash("admin123")))
            self._guardar_usuarios()
        if not self.productos:
            for n, p, s in [("Hamburguesa", 5.50, 30), ("Pizza personal", 6.00, 25),
                            ("Jugo natural", 2.00, 50), ("Ensalada", 4.25, 20)]:
                self.productos.append(Producto(self._siguiente_id(self.productos), n, p, s))
            self._guardar_productos()
        if not self.archivos.leer(self.F_VENTAS):
            self._guardar_ventas()

    def _guardar_usuarios(self):
        self.archivos.guardar(self.F_USUARIOS, [u.to_dict() for u in self.usuarios])

    def _guardar_productos(self):
        self.archivos.guardar(self.F_PRODUCTOS, [p.to_dict() for p in self.productos])

    def _guardar_ventas(self):
        self.archivos.guardar(self.F_VENTAS, [v.to_dict() for v in self.ventas])

    # ---------- autenticación y permisos ----------
    def autenticar(self, correo, clave):
        correo = correo.strip().lower()
        if not correo or not clave:
            raise ValueError("Ingrese correo y contraseña.")
        for u in self.usuarios:
            if u.correo.lower() == correo and u.clave_hash == self._hash(clave):
                return u
        raise ValueError("Credenciales incorrectas.")

    @staticmethod
    def puede_gestionar_usuarios(usuario):
        return usuario.rol == ADMIN

    @staticmethod
    def puede_gestionar_productos(usuario):
        return usuario.rol in (ADMIN, EMPLEADO)

    def _exigir_admin(self, actor):
        if not self.puede_gestionar_usuarios(actor):
            raise PermissionError("Solo el Administrador puede gestionar usuarios.")

    # ---------- usuarios (CRUD) ----------
    def listar_usuarios(self):
        return list(self.usuarios)

    def obtener_usuario(self, usuario_id):
        for u in self.usuarios:
            if u.id == usuario_id:
                return u
        raise ValueError("Usuario no encontrado.")

    def _validar_datos_usuario(self, nombre, correo, rol, clave, excluir_id=None, clave_obligatoria=True):
        if not nombre.strip():
            raise ValueError("El nombre es obligatorio.")
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", correo.strip()):
            raise ValueError("Correo electrónico no válido.")
        if rol not in self.ROLES_GESTIONABLES:
            raise ValueError("Seleccione un rol válido (Empleado o Cliente).")
        if clave_obligatoria or clave:
            if len(clave) < 4:
                raise ValueError("La contraseña debe tener al menos 4 caracteres.")
        for u in self.usuarios:
            if u.correo.lower() == correo.strip().lower() and u.id != excluir_id:
                raise ValueError("Ya existe un usuario con ese correo.")

    def registrar_usuario(self, actor, nombre, correo, rol, clave):
        self._exigir_admin(actor)
        self._validar_datos_usuario(nombre, correo, rol, clave)
        u = Usuario(self._siguiente_id(self.usuarios), nombre.strip(),
                    correo.strip().lower(), rol, self._hash(clave))
        self.usuarios.append(u)
        self._guardar_usuarios()
        return u

    def actualizar_usuario(self, actor, usuario_id, nombre, correo, rol, clave=""):
        self._exigir_admin(actor)
        u = self.obtener_usuario(usuario_id)
        if u.rol == ADMIN:
            raise ValueError("La cuenta de Administrador no se puede modificar.")
        self._validar_datos_usuario(nombre, correo, rol, clave, excluir_id=u.id, clave_obligatoria=False)
        u.nombre, u.correo, u.rol = nombre.strip(), correo.strip().lower(), rol
        if clave:
            u.clave_hash = self._hash(clave)
        self._guardar_usuarios()
        return u

    def eliminar_usuario(self, actor, usuario_id):
        self._exigir_admin(actor)
        u = self.obtener_usuario(usuario_id)
        if u.rol == ADMIN or u.id == actor.id:
            raise ValueError("No se puede eliminar al Administrador ni a la cuenta activa.")
        self.usuarios.remove(u)
        self._guardar_usuarios()

    # ---------- productos ----------
    def listar_productos(self):
        return list(self.productos)

    def agregar_producto(self, actor, nombre, precio, stock):
        if not self.puede_gestionar_productos(actor):
            raise PermissionError("No tiene permisos para gestionar productos.")
        if not nombre.strip():
            raise ValueError("El nombre del producto es obligatorio.")
        try:
            precio, stock = float(precio), int(stock)
        except ValueError:
            raise ValueError("Precio y stock deben ser numéricos.")
        if precio <= 0 or stock < 0:
            raise ValueError("Precio debe ser mayor a 0 y stock no negativo.")
        p = Producto(self._siguiente_id(self.productos), nombre.strip(), precio, stock)
        self.productos.append(p)
        self._guardar_productos()
        return p

    # ---------- ventas / pedidos ----------
    def registrar_venta(self, usuario, items):
        """items: lista de (producto_id, cantidad)."""
        if not items:
            raise ValueError("Agregue al menos un producto al pedido.")
        detalle, total = [], 0.0
        for pid, cant in items:
            prod = next((p for p in self.productos if p.id == pid), None)
            if prod is None:
                raise ValueError("Producto no encontrado.")
            if cant <= 0 or cant > prod.stock:
                raise ValueError(f"Stock insuficiente para {prod.nombre} (disponible: {prod.stock}).")
            sub = round(prod.precio * cant, 2)
            detalle.append({"producto_id": pid, "nombre": prod.nombre,
                            "cantidad": cant, "subtotal": sub})
            total += sub
        for d in detalle:
            next(p for p in self.productos if p.id == d["producto_id"]).stock -= d["cantidad"]
        v = Venta(self._siguiente_id(self.ventas), datetime.now().strftime("%Y-%m-%d %H:%M"),
                  usuario.id, detalle, round(total, 2))
        self.ventas.append(v)
        self._guardar_ventas()
        self._guardar_productos()
        return v

    def listar_ventas(self, usuario):
        if usuario.rol == CLIENTE:
            return [v for v in self.ventas if v.usuario_id == usuario.id]
        return list(self.ventas)
