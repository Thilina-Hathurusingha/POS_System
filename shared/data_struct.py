from dataclasses import dataclass

@dataclass
class Product:
    """Product data structure"""
    id: int
    name: str
    price: float
    category: int
    vendor: int
    stock: int

@dataclass
class Category:
    id: int
    name: str

@dataclass
class Vendor:
    id: int
    name: str