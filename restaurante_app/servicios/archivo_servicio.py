import json
import os


class ArchivoServicio:
    """Lectura y escritura de archivos JSON (persistencia)."""

    def __init__(self, carpeta=None):
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.carpeta = carpeta or os.path.join(base, "datos")
        os.makedirs(self.carpeta, exist_ok=True)

    def _ruta(self, nombre):
        return os.path.join(self.carpeta, nombre)

    def leer(self, nombre):
        try:
            with open(self._ruta(nombre), encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def guardar(self, nombre, datos):
        with open(self._ruta(nombre), "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
