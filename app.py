from flask import Flask
from flask_graphql import GraphQLView
from flask_cors import CORS
import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from sqlalchemy import create_engine, Column, Integer, String, Float, JSON
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
import time

# Import async fire-and-forget operations
from async_db import fire_and_forget_create, fire_and_forget_update

# Basic Flask setup
app = Flask(__name__)
app.config['DEBUG'] = True
CORS(app)

# Database setup - using sqlite
import os
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///products.db')
engine = create_engine(DATABASE_URL)
db_session = scoped_session(sessionmaker(bind=engine))

# Use the modern declarative_base from sqlalchemy.orm
Base = declarative_base()
Base.query = db_session.query_property()

# Product model
class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200))
    price = Column(Float)
    description = Column(String(1000))
    category = Column(String(100))
    image = Column(String(500))
    rating = Column(JSON)  # stores {"rate": float, "count": int}

# Create tables
Base.metadata.create_all(bind=engine)

# GraphQL Schema
class ProductObject(SQLAlchemyObjectType):
    class Meta:
        model = Product

class Query(graphene.ObjectType):
    # Get all products
    all_products = graphene.List(
        ProductObject,
        search=graphene.String(),
        first=graphene.Int(),
        skip=graphene.Int()
    )
    
    # Get single product by id
    product = graphene.Field(ProductObject, product_id=graphene.Int())
    
    def resolve_all_products(self, info, search=None, first=None, skip=0):
        """Generl Search Query"""
        query = Product.query
        
        if search:
            query = query.filter(
                Product.title.contains(search) | 
                Product.description.contains(search)
            )
        
        if skip:
            query = query.offset(skip)
        if first:
            query = query.limit(first)
            
        return query.all()
    
    def resolve_product(self, info, product_id):
        """Get single product by id"""
        return Product.query.filter_by(id=product_id).first()

class CreateProduct(graphene.Mutation):
    """Create Product Mutation"""
    class Arguments:
        title = graphene.String(required=True)
        price = graphene.Float(required=True)
        description = graphene.String()
        category = graphene.String()
        image = graphene.String()
        rating_rate = graphene.Float()
        rating_count = graphene.Int()
    
    # Return a status message instead of the product
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, title, price, description=None, category=None, 
               image=None, rating_rate=None, rating_count=None):
        """TRUE ASYNC insert - fire and forget, no waiting for ID"""
        
        # Build rating dict if provided
        rating = None
        if rating_rate is not None and rating_count is not None:
            rating = {"rate": rating_rate, "count": rating_count}
        
        # Prepare data for async insert
        product_data = {
            "title": title,
            "price": price,
            "description": description,
            "category": category,
            "image": image,
            "rating": rating
        }
        
        # Fire and forget - returns immediately without waiting
        fire_and_forget_create(product_data)
        
        # Return success status immediately
        # The actual database write happens in the background
        return CreateProduct(
            success=True, 
            message=f"Product '{title}' queued for creation"
        )

class UpdateProduct(graphene.Mutation):
    """Update Product Mutation"""
    class Arguments:
        product_id = graphene.Int(required=True)
        title = graphene.String()
        price = graphene.Float()
        description = graphene.String()
        category = graphene.String()
        image = graphene.String()
        rating_rate = graphene.Float()
        rating_count = graphene.Int()
    
    # Return status instead of the updated product
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, product_id, **kwargs):
        """Asynch DB update"""
        
        # Quick sync check if product exists
        product = Product.query.filter_by(id=product_id).first()
        
        if not product:
            return UpdateProduct(
                success=False, 
                message=f"Product with ID {product_id} not found"
            )
        
        # Prepare update data
        updates = {}
        
        if 'title' in kwargs:
            updates['title'] = kwargs['title']
        if 'price' in kwargs:
            updates['price'] = kwargs['price']
        if 'description' in kwargs:
            updates['description'] = kwargs['description']
        if 'category' in kwargs:
            updates['category'] = kwargs['category']
        if 'image' in kwargs:
            updates['image'] = kwargs['image']
        
        if 'rating_rate' in kwargs and 'rating_count' in kwargs:
            updates['rating'] = {
                "rate": kwargs['rating_rate'], 
                "count": kwargs['rating_count']
            }
        
        # Fire and forget - returns immediately without waiting
        fire_and_forget_update(product_id, updates)
        
        # Return success status immediately
        # The actual database write happens in the background
        return UpdateProduct(
            success=True,
            message=f"Product {product_id} queued for update"
        )

class CreateProductSync(graphene.Mutation):
    """Sync Insert for when you need the ID back"""
    class Arguments:
        title = graphene.String(required=True)
        price = graphene.Float(required=True)
        description = graphene.String()
        category = graphene.String()
        image = graphene.String()
        rating_rate = graphene.Float()
        rating_count = graphene.Int()
    
    product = graphene.Field(ProductObject)
    
    def mutate(self, info, title, price, description=None, category=None, 
               image=None, rating_rate=None, rating_count=None):
        """Sync Insert for when you need the product back immediately"""
        rating = None
        if rating_rate is not None and rating_count is not None:
            rating = {"rate": rating_rate, "count": rating_count}
        
        product = Product(
            title=title,
            price=price,
            description=description,
            category=category,
            image=image,
            rating=rating
        )
        
        db_session.add(product)
        db_session.commit()
        
        return CreateProductSync(product=product)

class Mutation(graphene.ObjectType):
    create_product = CreateProduct.Field()  # Asynch DB insert
    update_product = UpdateProduct.Field()  # Asynch DB update
    create_product_sync = CreateProductSync.Field()  # Sync Insert for when you need the ID back

# GraphQL Schema
schema = graphene.Schema(query=Query, mutation=Mutation)

# GraphQL Endpoint
app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=True  # Enable GraphiQL interface for testing
    )
)

# Health Check Endpoint
@app.route('/health')
def health_check():
    return {'status': 'ok'}

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == '__main__':
    # Add sample product
    if Product.query.count() == 0:
        sample_product = Product(
            title="Sample Laptop",
            price=999.99,
            description="A great laptop for developers",
            category="Electronics",
            image="https://example.com/laptop.jpg",
            rating={"rate": 4.5, "count": 120}
        )
        db_session.add(sample_product)
        db_session.commit()
        print("Added sample product")
    
    # Run on 0.0.0.0 for Docker compatibility
    app.run(host='0.0.0.0', debug=True, port=5000)
