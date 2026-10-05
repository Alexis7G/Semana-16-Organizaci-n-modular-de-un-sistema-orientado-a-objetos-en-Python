class Usuario:
    """Entidad de usuario. El atributo `rol` define sus permisos."""

    ROLES = ("Administrador", "Empleado", "Cliente")

    def __init__(self, id, nombre, correo, rol, clave_hash):
        self.id = id
        self.nombre = nombre
        self.correo = correo
        self.rol = rol
        self.clave_hash = clave_hash

    def to_dict(self):
        return {"id": self.id, "nombre": self.nombre, "correo": self.correo,
                "rol": self.rol, "clave_hash": self.clave_hash}

    @classmethod
    def from_dict(cls, d):
        return cls(d["id"], d["nombre"], d["correo"], d["rol"], d["clave_hash"])
