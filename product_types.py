"""
Type definitions for the product API
"""

from typing import TypedDict, Optional, Dict, Any, List

class RatingType(TypedDict):
    """Type definition for product rating"""
    rate: float
    count: int

class ProductType(TypedDict):
    """Type definition for a complete product"""
    id: int
    title: str
    price: float
    description: Optional[str]
    category: Optional[str]
    image: Optional[str]
    rating: Optional[RatingType]

class ProductCreateInput(TypedDict):
    """Type definition for creating a product"""
    title: str
    price: float
    description: Optional[str]
    category: Optional[str]
    image: Optional[str]
    rating_rate: Optional[float]
    rating_count: Optional[int]

class ProductUpdateInput(TypedDict, total=False):
    """Type definition for updating a product (all fields optional)"""
    title: str
    price: float
    description: str
    category: str
    image: str
    rating_rate: float
    rating_count: int

class PaginationParams(TypedDict):
    """Type definition for pagination parameters"""
    first: Optional[int]
    skip: int
    search: Optional[str]

# Type alias for GraphQL response
GraphQLResponse = Dict[str, Any]
