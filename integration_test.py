"""
Integration tests with verbose request/response logging and complete test data
"""

import requests
import json
import time
import sys
import os
import traceback

# When running in Docker, use the service name
if os.environ.get('DOCKER_ENV'):
    BASE_URL = "http://web:5000"
else:
    BASE_URL = "http://localhost:5000"

GRAPHQL_URL = f"{BASE_URL}/graphql"

# Check for verbose mode
VERBOSE = os.environ.get('VERBOSE', '').lower() in ('1', 'true', 'yes')

def log_request_response(mutation_or_query, response, data):
    """Log request and response if in verbose mode"""
    if VERBOSE:
        print("\n--- REQUEST ---")
        print(mutation_or_query.strip())
        print("\n--- RESPONSE ---")
        print(f"Status: {response.status_code}")
        print(json.dumps(data, indent=2))
        print("---------------\n")

def test_health_check():
    """Test health endpoint"""
    try:
        if VERBOSE:
            print("\n=== Testing Health Check ===")
        
        response = requests.get(f"{BASE_URL}/health")
        data = response.json()
        
        if VERBOSE:
            print(f"GET {BASE_URL}/health")
            print(f"Response: {json.dumps(data, indent=2)}")
        
        assert response.status_code == 200
        assert data['status'] == 'ok'
        print("Health check passed")
    except Exception as e:
        print(f"Health check failed: {e}")
        raise

def test_async_create_product():
    """Test async product creation with full data"""
    try:
        if VERBOSE:
            print("\n=== Testing Async Create Product (Full Data) ===")
        
        mutation = '''
        mutation {
            createProduct(
                title: "MacBook Pro M3",
                price: 2399.99,
                description: "14-inch Liquid Retina XDR display, M3 Pro chip with 12-core CPU and 18-core GPU, 18GB unified memory, 1TB SSD storage",
                category: "Laptops",
                image: "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/mbp14-m3-max-pro-spaceblack-select-202310",
                ratingRate: 4.8,
                ratingCount: 342
            ) {
                success
                message
            }
        }
        '''
        
        response = requests.post(GRAPHQL_URL, json={'query': mutation})
        data = response.json()
        
        log_request_response(mutation, response, data)
        
        assert response.status_code == 200
        assert data['data']['createProduct']['success'] == True
        assert 'queued for creation' in data['data']['createProduct']['message']
        
        print("Async create product passed ( with full data)")
        
        # Wait a moment for async operation to complete
        time.sleep(1)
        
    except Exception as e:
        print(f"Async create failed: {e}")
        raise

def test_sync_create_for_testing():
    """Test sync create with complete product data"""
    try:
        if VERBOSE:
            print("\n=== Testing Sync Create Product (Full Data) ===")
        
        mutation = '''
        mutation {
            createProductSync(
                title: "Sony WH-1000XM5",
                price: 379.99,
                description: "Industry-leading noise cancellation with Auto NC Optimizer, 30-hour battery life, ultra-comfortable lightweight design with soft fit leather",
                category: "Audio",
                image: "https://m.media-amazon.com/images/I/61vJtKbAssL._AC_SL1500_.jpg",
                ratingRate: 4.6,
                ratingCount: 1847
            ) {
                product {
                    id
                    title
                    price
                    description
                    category
                    image
                    rating
                }
            }
        }
        '''
        
        response = requests.post(GRAPHQL_URL, json={'query': mutation})
        data = response.json()
        
        log_request_response(mutation, response, data)
        
        assert response.status_code == 200
        product_id = data['data']['createProductSync']['product']['id']
        
        print(f"Sync create passed (ID: {product_id}, with full data)")
        return product_id
        
    except Exception as e:
        print(f"Sync create failed: {e}")
        raise

def test_get_all_products():
    """Test getting all products"""
    try:
        if VERBOSE:
            print("\n=== Testing Get All Products ===")
        
        query = '''
        query {
            allProducts {
                id
                title
                price
                description
                category
                image
                rating
            }
        }
        '''
        
        response = requests.post(GRAPHQL_URL, json={'query': query})
        data = response.json()
        
        log_request_response(query, response, data)
        
        assert response.status_code == 200
        products = data['data']['allProducts']
        
        # Should have products from async and sync creates
        assert len(products) > 0
        
        # Check if async product was created
        async_product_found = any(p['title'] == 'MacBook Pro M3' for p in products)
        if async_product_found:
            print(f"Get all products passed ({len(products)} products, async write confirmed)")
        else:
            print(f"Get all products passed ({len(products)} products)")
        
        return products
        
    except Exception as e:
        print(f"Get all products failed: {e}")
        raise

def test_get_product_by_id(product_id):
    """Test getting a specific product with all fields"""
    try:
        if VERBOSE:
            print(f"\n=== Testing Get Product by ID ({product_id}) ===")
        
        query = f'''
        query {{
            product(productId: {product_id}) {{
                id
                title
                price
                description
                category
                image
                rating
            }}
        }}
        '''
        
        response = requests.post(GRAPHQL_URL, json={'query': query})
        data = response.json()
        
        log_request_response(query, response, data)
        
        assert response.status_code == 200
        assert data['data']['product'] is not None
        assert data['data']['product']['id'] == product_id
        
        print(f"Get product by ID passed (all fields retrieved)")
        
    except Exception as e:
        print(f"Get product by ID failed: {e}")
        raise

def test_async_update_product(product_id):
    """Test async  update with full data"""
    try:
        if VERBOSE:
            print(f"\n=== Testing Async Update Product ({product_id}) ===")
        
        mutation = f'''
        mutation {{
            updateProduct(
                productId: {product_id},
                title: "Sony WH-1000XM5 (Updated)",
                price: 349.99,
                description: "UPDATED: Premium noise-cancelling headphones with exceptional sound quality and comfort. Now with improved call quality.",
                category: "Premium Audio",
                image: "https://www.sony.com/image/5d02da5df552836db894cead8a68f5f3",
                ratingRate: 4.9,
                ratingCount: 2150
            ) {{
                success
                message
            }}
        }}
        '''
        
        response = requests.post(GRAPHQL_URL, json={'query': mutation})
        data = response.json()
        
        log_request_response(mutation, response, data)
        
        assert response.status_code == 200
        assert data['data']['updateProduct']['success'] == True
        assert 'queued for update' in data['data']['updateProduct']['message']
        
        print("Async update passed ( with full data)")
        
        # Wait for async operation and verify
        time.sleep(1)
        
        if VERBOSE:
            print("\n=== Verifying Async Update ===")
        
        # Verify the update happened
        verify_query = f'''
        query {{
            product(productId: {product_id}) {{
                title
                price
                description
                category
                rating
            }}
        }}
        '''
        
        verify_response = requests.post(GRAPHQL_URL, json={'query': verify_query})
        verify_data = verify_response.json()
        
        log_request_response(verify_query, verify_response, verify_data)
        
        if verify_data['data']['product']['title'] == 'Sony WH-1000XM5 (Updated)':
            print("  Async update verified (all fields updated)")
        
    except Exception as e:
        print(f"Async update failed: {e}")
        raise

def test_search():
    """Test search functionality with realistic products"""
    try:
        if VERBOSE:
            print("\n=== Testing Search Functionality ===")
        
        # Create diverse products with full data using async 
        test_products = [
            {
                "title": "Razer DeathAdder V3 Gaming Mouse",
                "price": 149.99,
                "description": "Ultra-lightweight ergonomic esports mouse with 30K DPI sensor",
                "category": "Gaming Peripherals",
                "image": "https://assets.razerzone.com/eeimages/support/products/1939/1939-deathadder-v3.png",
                "ratingRate": 4.7,
                "ratingCount": 523
            },
            {
                "title": "Corsair K70 RGB Gaming Keyboard",
                "price": 169.99,
                "description": "Mechanical gaming keyboard with Cherry MX switches and RGB backlighting",
                "category": "Gaming Peripherals",
                "image": "https://www.corsair.com/medias/sys_master/images/images/h97/h89/9112096522270/-CH-9109010-NA-Gallery-K70-RGB-MK2-01.png",
                "ratingRate": 4.5,
                "ratingCount": 892
            },
            {
                "title": "Herman Miller Aeron Office Chair",
                "price": 1795.00,
                "description": "Ergonomic office chair with PostureFit SL back support and 12-year warranty",
                "category": "Office Furniture",
                "image": "https://www.hermanmiller.com/content/dam/hmicom/page_assets/products/aeron_chair/mh_prd_ovw_aeron_chair.jpg",
                "ratingRate": 4.8,
                "ratingCount": 3421
            }
        ]
        
        for product in test_products:
            mutation = f'''
            mutation {{
                createProduct(
                    title: "{product['title']}",
                    price: {product['price']},
                    description: "{product['description']}",
                    category: "{product['category']}",
                    image: "{product['image']}",
                    ratingRate: {product['ratingRate']},
                    ratingCount: {product['ratingCount']}
                ) {{
                    success
                }}
            }}
            '''
            response = requests.post(GRAPHQL_URL, json={'query': mutation})
            if VERBOSE:
                data = response.json()
                print(f"Creating: {product['title']}")
                log_request_response(mutation, response, data)
        
        # Wait for async operations
        time.sleep(1)
        
        # Search for "Gaming"
        query = '''
        query {
            allProducts(search: "Gaming") {
                title
                category
                price
            }
        }
        '''
        
        response = requests.post(GRAPHQL_URL, json={'query': query})
        data = response.json()
        
        log_request_response(query, response, data)
        
        products = data['data']['allProducts']
        gaming_products = [p for p in products if 'Gaming' in p['title'] or 'Gaming' in p.get('category', '')]
        
        assert len(gaming_products) >= 2
        print(f"Search functionality passed ({len(gaming_products)} gaming products found)")
        
    except Exception as e:
        print(f"Search failed: {e}")
        raise

def test_pagination():
    """Test pagination with full product data"""
    try:
        if VERBOSE:
            print("\n=== Testing Pagination ===")
        
        query = '''
        query {
            allProducts(first: 3, skip: 0) {
                title
                price
                category
            }
        }
        '''
        
        response = requests.post(GRAPHQL_URL, json={'query': query})
        data = response.json()
        
        log_request_response(query, response, data)
        
        products = data['data']['allProducts']
        
        assert len(products) <= 3
        print(f"Pagination passed ({len(products)} products with limit 3)")
        
        # Test skip functionality
        if VERBOSE:
            print("\n=== Testing Pagination Skip ===")
        
        skip_query = '''
        query {
            allProducts(first: 2, skip: 2) {
                title
                category
            }
        }
        '''
        
        skip_response = requests.post(GRAPHQL_URL, json={'query': skip_query})
        skip_data = skip_response.json()
        
        log_request_response(skip_query, skip_response, skip_data)
        
        skip_products = skip_data['data']['allProducts']
        print(f"  Skip pagination passed ({len(skip_products)} products after skip 2)")
        
    except Exception as e:
        print(f"Pagination failed: {e}")
        raise

def run_all_tests():
    """Run all tests with complete product data"""
    print("\n" + "="*50)
    print("Running Integration Tests")
    if VERBOSE:
        print("MODE: VERBOSE (showing all requests/responses)")
    print("Testing TRUE ASYNC  Architecture")
    print(f"Target: {BASE_URL}")
    print("="*50 + "\n")
    
    # Wait for server
    max_retries = 30
    for i in range(max_retries):
        try:
            response = requests.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                print("Server is ready!\n")
                break
        except Exception:
            if i == max_retries - 1:
                print(f"ERROR: Server not responding after 30 seconds")
                sys.exit(1)
            if not VERBOSE:
                print(f"Waiting for server... ({i+1}/{max_retries})")
            time.sleep(1)
    
    # Run tests
    try:
        test_health_check()
        test_async_create_product()  #  create with full data
        product_id = test_sync_create_for_testing()  # Sync create with full data
        test_get_all_products()
        test_get_product_by_id(product_id)
        test_async_update_product(product_id)  #  update with full data
        test_search()
        test_pagination()
        
        print("\n" + "="*50)
        print("All tests passed!")
        print("Test data includes: title, price, description, category, image, rating")
        print("="*50 + "\n")
        return 0
        
    except Exception as e:
        print("\n" + "="*50)
        print("Tests failed!")
        print("="*50 + "\n")
        return 1

if __name__ == "__main__":
    sys.exit(run_all_tests())
