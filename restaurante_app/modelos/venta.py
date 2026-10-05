class Venta:
    """items: lista de dicts {producto_id, nombre, cantidad, subtotal}."""

    def __init__(self, id, fecha, usuario_id, items, total):
        self.id = id
        self.fecha = fecha
        self.usuario_id = usuario_id
        self.items = items
        self.total = total

    def to_dict(self):
        return {"id": self.id, "fecha": self.fecha, "usuario_id": self.usuario_id,
                "items": self.items, "total": self.total}

    @classmethod
    def from_dict(cls, d):
        return cls(d["id"], d["fecha"], d["usuario_id"], d["items"], d["total"])
