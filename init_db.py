"""
Initialize the database with some sample data for testing
Run this after starting the app for the first time
"""

from app import db_session, Product
import random

def init_sample_data():
    """Add some sample products to the database"""
    
    # Check if we already have data
    existing = Product.query.count()
    if existing > 0:
        print(f"Database already has {existing} products. Skipping initialization.")
        return
    
    # Sample product data
    products = [
        {
            "title": "MacBook Pro 14",
            "price": 1999.99,
            "description": "Apple M3 Pro chip, 18GB RAM, 512GB SSD",
            "category": "Laptops",
            "image": "https://example.com/macbook.jpg",
            "rating": {"rate": 4.7, "count": 234}
        },
        {
            "title": "iPhone 15 Pro",
            "price": 1099.00,
            "description": "128GB, Titanium finish, A17 Pro chip",
            "category": "Smartphones",
            "image": "https://example.com/iphone.jpg",
            "rating": {"rate": 4.6, "count": 512}
        },
        {
            "title": "Sony WH-1000XM5",
            "price": 399.99,
            "description": "Wireless noise cancelling headphones",
            "category": "Audio",
            "image": "https://example.com/sony-headphones.jpg",
            "rating": {"rate": 4.5, "count": 189}
        },
        {
            "title": "Samsung 65\" OLED TV",
            "price": 1799.99,
            "description": "4K Smart TV with HDR10+",
            "category": "TVs",
            "image": "https://example.com/samsung-tv.jpg",
            "rating": {"rate": 4.4, "count": 95}
        },
        {
            "title": "Logitech MX Master 3S",
            "price": 99.99,
            "description": "Advanced wireless mouse for productivity",
            "category": "Accessories",
            "image": "https://example.com/mx-master.jpg",
            "rating": {"rate": 4.8, "count": 421}
        },
        {
            "title": "iPad Air",
            "price": 599.00,
            "description": "10.9-inch, M1 chip, 64GB",
            "category": "Tablets",
            "image": "https://example.com/ipad-air.jpg",
            "rating": {"rate": 4.6, "count": 312}
        },
        {
            "title": "Dell XPS 15",
            "price": 1499.99,
            "description": "Intel i7, 16GB RAM, 512GB SSD, RTX 4050",
            "category": "Laptops",
            "image": "https://example.com/dell-xps.jpg",
            "rating": {"rate": 4.3, "count": 167}
        },
        {
            "title": "Nintendo Switch OLED",
            "price": 349.99,
            "description": "7-inch OLED screen, enhanced audio",
            "category": "Gaming",
            "image": "https://example.com/switch.jpg",
            "rating": {"rate": 4.7, "count": 892}
        },
        {
            "title": "Kindle Paperwhite",
            "price": 149.99,
            "description": "6.8\" display, adjustable warm light, waterproof",
            "category": "E-readers",
            "image": "https://example.com/kindle.jpg",
            "rating": {"rate": 4.5, "count": 523}
        },
        {
            "title": "Bose QuietComfort Earbuds",
            "price": 279.00,
            "description": "True wireless with active noise cancelling",
            "category": "Audio",
            "image": "https://example.com/bose-earbuds.jpg",
            "rating": {"rate": 4.4, "count": 276}
        }
    ]
    
    # Add products to database
    for product_data in products:
        product = Product(
            title=product_data["title"],
            price=product_data["price"],
            description=product_data["description"],
            category=product_data["category"],
            image=product_data["image"],
            rating=product_data["rating"]
        )
        db_session.add(product)
    
    # Commit all products
    db_session.commit()
    print(f"Successfully added {len(products)} sample products to the database!")

if __name__ == "__main__":
    init_sample_data()
