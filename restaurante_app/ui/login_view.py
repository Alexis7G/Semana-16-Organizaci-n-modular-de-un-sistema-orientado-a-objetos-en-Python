import os
import tkinter as tk
from tkinter import ttk, messagebox

ASSETS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")


def cargar_logo(nombre="logo.png"):
    try:
        return tk.PhotoImage(file=os.path.join(ASSETS, nombre))
    except tk.TclError:
        return None


class LoginView(ttk.Frame):
    """Pantalla de inicio de sesión. Valida mediante RestauranteServicio."""

    def __init__(self, master, servicio, al_autenticar):
        super().__init__(master, padding=30)
        self.servicio = servicio
        self.al_autenticar = al_autenticar
        self.pack(expand=True)

        self.logo = cargar_logo()
        if self.logo:
            ttk.Label(self, image=self.logo).pack(pady=(0, 8))
        ttk.Label(self, text="Restaurante App", font=("Segoe UI", 18, "bold")).pack()
        ttk.Label(self, text="Inicie sesión para continuar").pack(pady=(0, 15))

        self.var_correo = tk.StringVar()
        self.var_clave = tk.StringVar()
        ttk.Label(self, text="Correo").pack(anchor="w")
        self.ent_correo = ttk.Entry(self, textvariable=self.var_correo, width=32)
        self.ent_correo.pack(pady=(0, 8))
        ttk.Label(self, text="Contraseña").pack(anchor="w")
        self.ent_clave = ttk.Entry(self, textvariable=self.var_clave, show="*", width=32)
        self.ent_clave.pack(pady=(0, 12))

        ttk.Button(self, text="Ingresar", command=self.iniciar_sesion).pack(fill="x")
        ttk.Label(self, text="Admin por defecto: admin@restaurante.com / admin123",
                  foreground="gray").pack(pady=(12, 0))

        # Eventos de teclado
        self.ent_correo.bind("<Return>", lambda e: self.ent_clave.focus())
        self.ent_clave.bind("<Return>", self.iniciar_sesion)
        self.ent_correo.focus()

    def iniciar_sesion(self, event=None):
        try:
            usuario = self.servicio.autenticar(self.var_correo.get(), self.var_clave.get())
        except ValueError as e:
            messagebox.showerror("Acceso denegado", str(e))
            return
        self.al_autenticar(usuario)
