from dataclasses import dataclass

@dataclass
class Product:
    """Product data structure"""
    id: int
    name: str
    description: str
    price: float
    category: int
    vendor: int
    stock: int
    batch_id: int
    cost: float

@dataclass
class Category:
    id: int
    name: str

@dataclass
class Vendor:
    id: int
    name: str

@dataclass
class Batch:
    batch_id: int
    item_code: int
    cost: float
    mrp: float
    price: float
    quantity: int
    in_stock: int