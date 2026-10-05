import tkinter as tk
from tkinter import ttk

from servicios.restaurante_servicio import RestauranteServicio
from ui.login_view import LoginView, cargar_logo
from ui.main_view import MainView


class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Restaurante App")
        self.root.geometry("820x560")
        ttk.Style().theme_use("clam")
        icono = cargar_logo("logo_small.png")
        if icono:
            self.root.iconphoto(True, icono)
            self._icono = icono
        self.servicio = RestauranteServicio()
        self.mostrar_login()

    def _limpiar(self):
        for w in self.root.winfo_children():
            w.destroy()

    def mostrar_login(self):
        self._limpiar()
        LoginView(self.root, self.servicio, self.mostrar_principal)

    def mostrar_principal(self, usuario):
        self._limpiar()
        MainView(self.root, self.servicio, usuario, self.mostrar_login)

    def ejecutar(self):
        self.root.mainloop()


if __name__ == "__main__":
    App().ejecutar()
