class Producto:
    def __init__(self, id, nombre, precio, stock):
        self.id = id
        self.nombre = nombre
        self.precio = precio
        self.stock = stock

    def to_dict(self):
        return {"id": self.id, "nombre": self.nombre,
                "precio": self.precio, "stock": self.stock}

    @classmethod
    def from_dict(cls, d):
        return cls(d["id"], d["nombre"], d["precio"], d["stock"])
