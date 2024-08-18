from enum import Enum


Categories = {
    "R": "Resistors",
    "L": "Inductors",
    "C": "Capacitors",
    "Q": "Transistors",
    "D": "Diodes",
}


class ColumnName(Enum):
    ID = "ID"
    NAME = "Name"
    DESIGNATOR = "Designator"
    FOOTPRINT = "Footprint"
    QUANTITY = "Quantity"
    MANUFACTURER_PART = "Manufacturer Part"
    MANUFACTURER = "Manufacturer"
    SUPPLIER = "Supplier"
    SUPPLIER_PART = "Supplier Part"
    PRICE = "Price"


class ComponentType(Enum):
    RESISTOR = "R"
    INDUCTOR = "L"
    CAPACITOR = "C"
    TRANSISTOR = "Q"
    DIODE = "D"
    INTEGRATED_CIRCUIT = "U"
    FUSE = "F"
    CONNECTOR = ["J", "CON"]


BASIC_TYPES = [
    ComponentType.CAPACITOR,
    ComponentType.RESISTOR,
    ComponentType.INDUCTOR,
    ComponentType.DIODE,
    ComponentType.TRANSISTOR
]


class Component:
    def __init__(self, name: str, designators: list, footprint: str, quantity: int, typeof: ComponentType):
        self.name = name
        self.designators = designators
        self.footprint = footprint
        self.quantity = quantity
        self.typeof = typeof

    def printout(self, index: int = None):
        if index:
            print(f"\nLP: {index}, Type: {self.typeof.name}, Name: {self.name}, Footprint: {self.footprint}, Quantity: "
                  f"{self.quantity}, Designators: {self.designators}")
        else:
            print(f"\nType: {self.typeof.name}, Name: {self.name}, Footprint: {self.footprint}, Quantity: "
                  f"{self.quantity}, Designators: {self.designators}")


class Product:
    def __init__(self, symbol: str, description: str, producer: str, min_amount: int, stock: int, price: float):
        self.symbol = symbol
        self.description = description
        self.producer = producer
        self.min_amount = min_amount
        self.stock = stock
        self.price = price

    def printout(self, prefix: str, needed: int, to_buy: int):
        print(f"{prefix} '{self.symbol}': '{self.description}' by {self.producer} === needed: {needed}, minAmount: "
              f"{self.min_amount}, price: {self.price:.2f} PLN, total: {self.price * to_buy:.2f} PLN === stock: "
              f"{self.stock}")
