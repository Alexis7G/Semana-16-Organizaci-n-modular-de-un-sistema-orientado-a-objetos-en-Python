import tkinter as tk
from tkinter import ttk, messagebox

from ui.login_view import cargar_logo


class MainView(ttk.Frame):
    """Ventana principal: navegación por pestañas según el rol."""

    def __init__(self, master, servicio, usuario, al_cerrar_sesion):
        super().__init__(master, padding=10)
        self.servicio = servicio
        self.usuario = usuario
        self.al_cerrar_sesion = al_cerrar_sesion
        self.carrito = []  # [(producto_id, nombre, cantidad, subtotal)]
        self.pack(fill="both", expand=True)

        self._crear_cabecera()
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, pady=(10, 0))
        self._crear_tab_productos()
        self._crear_tab_ventas()
        if self.servicio.puede_gestionar_usuarios(usuario):
            self._crear_tab_usuarios()

    # ------------------------------------------------------------ cabecera
    def _crear_cabecera(self):
        barra = ttk.Frame(self)
        barra.pack(fill="x")
        self.logo = cargar_logo("logo_small.png")
        if self.logo:
            ttk.Label(barra, image=self.logo).pack(side="left", padx=(0, 8))
        ttk.Label(barra, text="Restaurante App", font=("Segoe UI", 14, "bold")).pack(side="left")
        ttk.Button(barra, text="Cerrar sesión", command=self.al_cerrar_sesion).pack(side="right")
        ttk.Label(barra, text=f"{self.usuario.nombre}  ·  {self.usuario.rol}").pack(side="right", padx=12)

    # ----------------------------------------------------------- productos
    def _crear_tab_productos(self):
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text="Productos")
        self.tree_prod = ttk.Treeview(tab, columns=("id", "nombre", "precio", "stock"),
                                      show="headings", height=10)
        for col, txt, w in (("id", "ID", 50), ("nombre", "Producto", 220),
                            ("precio", "Precio", 90), ("stock", "Stock", 80)):
            self.tree_prod.heading(col, text=txt)
            self.tree_prod.column(col, width=w, anchor="center" if col != "nombre" else "w")
        self.tree_prod.pack(fill="both", expand=True)

        if self.servicio.puede_gestionar_productos(self.usuario):
            f = ttk.LabelFrame(tab, text="Nuevo producto", padding=8)
            f.pack(fill="x", pady=(10, 0))
            self.var_pn, self.var_pp, self.var_ps = tk.StringVar(), tk.StringVar(), tk.StringVar()
            for i, (txt, var) in enumerate((("Nombre", self.var_pn), ("Precio", self.var_pp),
                                            ("Stock", self.var_ps))):
                ttk.Label(f, text=txt).grid(row=0, column=i * 2, padx=4)
                e = ttk.Entry(f, textvariable=var, width=14)
                e.grid(row=0, column=i * 2 + 1, padx=4)
                e.bind("<Return>", self.al_agregar_producto)
            ttk.Button(f, text="Agregar", command=self.al_agregar_producto).grid(row=0, column=6, padx=8)
        self.refrescar_productos()

    def refrescar_productos(self):
        self.tree_prod.delete(*self.tree_prod.get_children())
        for p in self.servicio.listar_productos():
            self.tree_prod.insert("", "end", iid=str(p.id),
                                  values=(p.id, p.nombre, f"${p.precio:.2f}", p.stock))
        if hasattr(self, "cb_producto"):
            self.cb_producto["values"] = [p.nombre for p in self.servicio.listar_productos()]

    def al_agregar_producto(self, event=None):
        try:
            self.servicio.agregar_producto(self.usuario, self.var_pn.get(),
                                           self.var_pp.get(), self.var_ps.get())
        except (ValueError, PermissionError) as e:
            messagebox.showerror("Error", str(e))
            return
        for v in (self.var_pn, self.var_pp, self.var_ps):
            v.set("")
        self.refrescar_productos()

    # -------------------------------------------------------------- ventas
    def _crear_tab_ventas(self):
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text="Pedidos")

        f = ttk.LabelFrame(tab, text="Nuevo pedido", padding=8)
        f.pack(fill="x")
        self.var_prod_sel, self.var_cant = tk.StringVar(), tk.IntVar(value=1)
        ttk.Label(f, text="Producto").grid(row=0, column=0, padx=4)
        self.cb_producto = ttk.Combobox(f, textvariable=self.var_prod_sel, state="readonly", width=22)
        self.cb_producto.grid(row=0, column=1, padx=4)
        ttk.Label(f, text="Cantidad").grid(row=0, column=2, padx=4)
        ttk.Spinbox(f, from_=1, to=99, textvariable=self.var_cant, width=5).grid(row=0, column=3, padx=4)
        ttk.Button(f, text="Añadir", command=self.al_anadir_carrito).grid(row=0, column=4, padx=8)

        self.tree_carrito = ttk.Treeview(tab, columns=("nombre", "cant", "sub"),
                                         show="headings", height=4)
        for col, txt in (("nombre", "Producto"), ("cant", "Cant."), ("sub", "Subtotal")):
            self.tree_carrito.heading(col, text=txt)
            self.tree_carrito.column(col, width=140, anchor="center")
        self.tree_carrito.pack(fill="x", pady=8)

        pie = ttk.Frame(tab)
        pie.pack(fill="x")
        self.lbl_total = ttk.Label(pie, text="Total: $0.00", font=("Segoe UI", 11, "bold"))
        self.lbl_total.pack(side="left")
        ttk.Button(pie, text="Registrar pedido", command=self.al_registrar_venta).pack(side="right")
        ttk.Button(pie, text="Vaciar", command=self.al_vaciar_carrito).pack(side="right", padx=6)

        ttk.Label(tab, text="Historial", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(10, 2))
        self.tree_ventas = ttk.Treeview(tab, columns=("id", "fecha", "total"), show="headings", height=5)
        for col, txt in (("id", "N°"), ("fecha", "Fecha"), ("total", "Total")):
            self.tree_ventas.heading(col, text=txt)
            self.tree_ventas.column(col, width=140, anchor="center")
        self.tree_ventas.pack(fill="both", expand=True)
        self.cb_producto["values"] = [p.nombre for p in self.servicio.listar_productos()]
        self.refrescar_ventas()

    def al_anadir_carrito(self):
        prod = next((p for p in self.servicio.listar_productos()
                     if p.nombre == self.var_prod_sel.get()), None)
        if prod is None:
            messagebox.showwarning("Pedido", "Seleccione un producto.")
            return
        try:
            cant = int(self.var_cant.get())
        except (tk.TclError, ValueError):
            messagebox.showwarning("Pedido", "Cantidad no válida.")
            return
        self.carrito.append((prod.id, prod.nombre, cant, round(prod.precio * cant, 2)))
        self._refrescar_carrito()

    def al_vaciar_carrito(self):
        self.carrito.clear()
        self._refrescar_carrito()

    def _refrescar_carrito(self):
        self.tree_carrito.delete(*self.tree_carrito.get_children())
        for _, n, c, s in self.carrito:
            self.tree_carrito.insert("", "end", values=(n, c, f"${s:.2f}"))
        self.lbl_total.config(text=f"Total: ${sum(x[3] for x in self.carrito):.2f}")

    def al_registrar_venta(self):
        try:
            self.servicio.registrar_venta(self.usuario, [(p, c) for p, _, c, _ in self.carrito])
        except ValueError as e:
            messagebox.showerror("Pedido", str(e))
            return
        self.carrito.clear()
        self._refrescar_carrito()
        self.refrescar_productos()
        self.refrescar_ventas()
        messagebox.showinfo("Pedido", "Pedido registrado correctamente.")

    def refrescar_ventas(self):
        self.tree_ventas.delete(*self.tree_ventas.get_children())
        for v in self.servicio.listar_ventas(self.usuario):
            self.tree_ventas.insert("", "end", values=(v.id, v.fecha, f"${v.total:.2f}"))

    # ------------------------------------------------------------ usuarios
    def _crear_tab_usuarios(self):
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text="Usuarios")

        izq = ttk.Frame(tab)
        izq.pack(side="left", fill="both", expand=True)
        self.tree_usr = ttk.Treeview(izq, columns=("id", "nombre", "correo", "rol"),
                                     show="headings", height=14, selectmode="browse")
        for col, txt, w in (("id", "ID", 40), ("nombre", "Nombre", 140),
                            ("correo", "Correo", 190), ("rol", "Rol", 110)):
            self.tree_usr.heading(col, text=txt)
            self.tree_usr.column(col, width=w, anchor="w")
        sb = ttk.Scrollbar(izq, orient="vertical", command=self.tree_usr.yview)
        self.tree_usr.configure(yscrollcommand=sb.set)
        self.tree_usr.pack(side="left", fill="both", expand=True)
        sb.pack(side="left", fill="y")

        der = ttk.LabelFrame(tab, text="Datos del usuario", padding=10)
        der.pack(side="left", fill="y", padx=(10, 0))
        self.var_un, self.var_uc = tk.StringVar(), tk.StringVar()
        self.var_uk, self.var_ur = tk.StringVar(), tk.StringVar()
        self.ent_nombre = self._campo(der, "Nombre", self.var_un)
        self.ent_correo = self._campo(der, "Correo", self.var_uc)
        self.ent_clave = self._campo(der, "Contraseña", self.var_uk, show="*")
        ttk.Label(der, text="Rol").pack(anchor="w")
        self.cb_rol = ttk.Combobox(der, textvariable=self.var_ur, state="readonly",
                                   values=self.servicio.ROLES_GESTIONABLES, width=26)
        self.cb_rol.pack(pady=(0, 6))
        self.lbl_info_rol = ttk.Label(der, text="", foreground="gray", wraplength=200)
        self.lbl_info_rol.pack(anchor="w", pady=(0, 8))

        for txt, cmd in (("Registrar", self.al_registrar_usuario),
                         ("Actualizar", self.al_actualizar_usuario),
                         ("Eliminar", self.al_eliminar_usuario),
                         ("Limpiar", self.al_limpiar_formulario)):
            ttk.Button(der, text=txt, command=cmd).pack(fill="x", pady=2)

        # ---- Eventos con bind() ----
        self.tree_usr.bind("<<TreeviewSelect>>", self.al_seleccionar_usuario)
        self.cb_rol.bind("<<ComboboxSelected>>", self.al_cambiar_rol)
        for w in (self.ent_nombre, self.ent_correo, self.ent_clave, self.cb_rol):
            w.bind("<Return>", self.al_registrar_usuario)
            w.bind("<Escape>", self.al_limpiar_formulario)
        self.tree_usr.bind("<Escape>", self.al_limpiar_formulario)
        self.refrescar_usuarios()

    @staticmethod
    def _campo(padre, texto, var, show=None):
        ttk.Label(padre, text=texto).pack(anchor="w")
        e = ttk.Entry(padre, textvariable=var, show=show, width=28)
        e.pack(pady=(0, 6))
        return e

    def refrescar_usuarios(self):
        self.tree_usr.delete(*self.tree_usr.get_children())
        for u in self.servicio.listar_usuarios():
            self.tree_usr.insert("", "end", iid=str(u.id), values=(u.id, u.nombre, u.correo, u.rol))

    # callbacks: capturan el evento y delegan en RestauranteServicio
    def al_seleccionar_usuario(self, event=None):
        sel = self.tree_usr.selection()
        if not sel:
            return
        u = self.servicio.obtener_usuario(int(sel[0]))  # solo el identificador
        self.var_un.set(u.nombre)
        self.var_uc.set(u.correo)
        self.var_uk.set("")
        self.var_ur.set(u.rol)
        self.al_cambiar_rol()

    def al_cambiar_rol(self, event=None):
        info = {"Administrador": "Acceso total, incluida la gestión de usuarios.",
                "Empleado": "Gestiona productos y registra pedidos.",
                "Cliente": "Consulta productos y ve sus propios pedidos."}
        self.lbl_info_rol.config(text=info.get(self.var_ur.get(), ""))

    def _id_seleccionado(self):
        sel = self.tree_usr.selection()
        if not sel:
            messagebox.showwarning("Usuarios", "Seleccione un usuario de la tabla.")
            return None
        return int(sel[0])

    def al_registrar_usuario(self, event=None):
        try:
            self.servicio.registrar_usuario(self.usuario, self.var_un.get(), self.var_uc.get(),
                                            self.var_ur.get(), self.var_uk.get())
        except (ValueError, PermissionError) as e:
            messagebox.showerror("Usuarios", str(e))
            return
        self.refrescar_usuarios()
        self.al_limpiar_formulario()

    def al_actualizar_usuario(self):
        uid = self._id_seleccionado()
        if uid is None:
            return
        try:
            self.servicio.actualizar_usuario(self.usuario, uid, self.var_un.get(), self.var_uc.get(),
                                             self.var_ur.get(), self.var_uk.get())
        except (ValueError, PermissionError) as e:
            messagebox.showerror("Usuarios", str(e))
            return
        self.refrescar_usuarios()
        self.al_limpiar_formulario()

    def al_eliminar_usuario(self):
        uid = self._id_seleccionado()
        if uid is None:
            return
        if not messagebox.askyesno("Confirmar", "¿Eliminar el usuario seleccionado?"):
            return
        try:
            self.servicio.eliminar_usuario(self.usuario, uid)
        except (ValueError, PermissionError) as e:
            messagebox.showerror("Usuarios", str(e))
            return
        self.refrescar_usuarios()
        self.al_limpiar_formulario()

    def al_limpiar_formulario(self, event=None):
        for v in (self.var_un, self.var_uc, self.var_uk, self.var_ur):
            v.set("")
        self.tree_usr.selection_remove(self.tree_usr.selection())
        self.lbl_info_rol.config(text="")
        self.ent_nombre.focus()
