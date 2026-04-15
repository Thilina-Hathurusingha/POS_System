from dataclasses import dataclass

@dataclass
class Product:
    """Product data structure"""
    id: int
    name: str
    price: float
    category: str
    vendor: str
    stock: int

@dataclass
class Category:
    id: int
    name: str

@dataclass
class Vendor:
    id: int
    name: str