# Restaurante App – Semana 16

Sistema de gestión de pedidos de un restaurante en **Python + Tkinter**, organizado de forma modular.
En esta semana se evoluciona la **gestión de usuarios** con manejo de eventos sobre un `Treeview`.

## Ejecución
```bash
python main.py
```
Requiere Python 3.8+ (Tkinter incluido). Usuario inicial: `admin@restaurante.com` / `admin123`.

## Estructura
```
restaurante_app/
├── datos/        productos.json, usuarios.json, ventas.json
├── modelos/      producto.py, usuario.py (con rol), venta.py
├── servicios/    archivo_servicio.py (JSON), restaurante_servicio.py (lógica y validaciones)
├── ui/           login_view.py, main_view.py
├── assets/       logo.png, logo_small.png
└── main.py
```

## Roles
| Rol | Permisos |
|---|---|
| Administrador | Todo, incluida la sección **Usuarios** |
| Empleado | Gestiona productos y registra pedidos |
| Cliente | Consulta productos y sus propios pedidos |

## Gestión de usuarios (solo Administrador)
CRUD completo (registrar, consultar, actualizar, eliminar) sobre un `Treeview` con formulario.
Solo se pueden crear usuarios Empleado y Cliente. Se valida nombre, correo (formato y único) y contraseña (mínimo 4).
Las contraseñas se guardan como hash SHA-256 en `usuarios.json`.

## Eventos implementados
| Evento | Mecanismo | Callback |
|---|---|---|
| Selección de fila | `bind("<<TreeviewSelect>>")` | `al_seleccionar_usuario` – carga el usuario por su identificador |
| Enter | `bind("<Return>")` | `al_registrar_usuario` |
| Escape | `bind("<Escape>")` | `al_limpiar_formulario` |
| Cambio de rol | `bind("<<ComboboxSelected>>")` | `al_cambiar_rol` |
| Botones | `command=` | Registrar, Actualizar, Eliminar, Limpiar |

Flujo: interacción → evento → `bind()`/`command` → callback → `RestauranteServicio` → persistencia JSON → actualización del `Treeview`.
La interfaz no contiene lógica de negocio: todo se delega en `RestauranteServicio`.
