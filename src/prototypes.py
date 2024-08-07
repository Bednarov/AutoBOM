from enum import Enum


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
    CONNECTOR = "J"


class Component:
    def __init__(self, name: str, designators: list, footprint: str, quantity: int, typeof: ComponentType):
        self.name = name
        self.designators = designators
        self.footprint = footprint
        self.quantity = quantity
        self.typeof = typeof

    def printout(self, index: int = None):
        if index:
            print(f"LP: {index}, Type: {self.typeof}, Name: {self.name}, Footprint: {self.footprint}, Quantity: "
                  f"{self.quantity}, Designators: {self.designators}")
        else:
            print(f"Type: {self.typeof}, Name: {self.name}, Footprint: {self.footprint}, Quantity: "
                  f"{self.quantity}, Designators: {self.designators}")
