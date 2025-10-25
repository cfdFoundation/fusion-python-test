# Product GraphQL API - Flask Backend with Async Task Queue

A Flask-based GraphQL API demonstrating a hybrid sync/async architecture with operations and synchronous reads.

## Quick Start

```bash
# Build and start the application
docker-compose up --build

# Or use helper scripts
./docker.sh fresh    # Linux/Mac
docker.bat fresh     # Windows

# Access GraphQL Playground
http://localhost:5000/graphql
```

## Helper Scripts

Both `docker.bat` (Windows) and `docker.sh` (Linux/Mac) provide identical functionality:

### Main Commands

```bash
# Start application
docker.bat up              # Start in foreground (see logs)
docker.bat start           # Start in background
docker.bat stop            # Stop application

# Testing
docker.bat test            # Run tests (quiet mode)
docker.bat test-verbose    # Show all requests/responses
docker.bat test-debug      # Full debug with server logs

# Quick access
docker.bat graphql         # Open GraphQL playground in browser
docker.bat logs            # View application logs
```

### Maintenance Commands

```bash
# Build and cleanup
docker.bat build           # Build Docker image (no cache)
docker.bat clean           # Remove all containers, volumes, networks
docker.bat fresh           # Clean rebuild and start
docker.bat restart         # Stop and restart cleanly

# Development
docker.bat shell           # Open bash shell in container
docker.bat init-db         # Initialize sample data
```

### Special Commands

```bash
# Demo mode - perfect for presentations
docker.bat demo            # Runs app and tests with full verbose output
```

### Complete Command Reference

| Command | Description | Use Case |
|---------|-------------|----------|
| `up` | Start app in foreground | Development - see logs |
| `start` | Start app in background | Normal usage |
| `stop` | Stop all containers | Clean shutdown |
| `test` | Run integration tests | Quick validation |
| `test-verbose` | Tests with request/response logs | Debug API calls |
| `test-debug` | Tests + server logs | Full debugging |
| `build` | Build image (no cache) | Force rebuild |
| `clean` | Remove everything | Start fresh |
| `fresh` | Clean + rebuild + start | Complete reset |
| `restart` | Stop + start | Quick restart |
| `shell` | Bash in container | Run commands |
| `init-db` | Add sample data | Populate database |
| `logs` | Follow logs | Monitor app |
| `graphql` | Open playground | Test queries |
| `demo` | Full demo mode | Show functionality |

### Linux/Mac Setup

```bash
# Make script executable (one time only)
chmod +x docker.sh

# Then use same commands
./docker.sh test-verbose
```

## API Features

### Queries (Synchronous)

#### Get All Products
```graphql
query {
  allProducts(search: "laptop", first: 10, skip: 0) {
    id
    title
    price
    description
    category
    image
    rating
  }
}
```

#### Get Product by ID
```graphql
query {
  product(productId: 1) {
    id
    title
    price
    description
    category
    image
    rating
  }
}
```

### Mutations

#### Create Product (Async - Fire & Forget)
```graphql
mutation {
  createProduct(
    title: "MacBook Pro M3",
    price: 2399.99,
    description: "14-inch Liquid Retina XDR display",
    category: "Laptops",
    image: "https://example.com/macbook.jpg",
    ratingRate: 4.8,
    ratingCount: 342
  ) {
    success
    message  # Returns immediately without waiting for DB write
  }
}
```

#### Create Product Sync (When you need the ID)
```graphql
mutation {
  createProductSync(
    title: "Sony Headphones",
    price: 379.99
  ) {
    product {
      id  # Returns with actual ID after DB write
      title
    }
  }
}
```

#### Update Product (Async - Fire & Forget)
```graphql
mutation {
  updateProduct(
    productId: 1,
    title: "Updated Title",
    price: 1999.99
  ) {
    success
    message  # Returns immediately
  }
}
```

## Testing

### Test Modes

The test suite supports three modes for different needs:

#### 1. Normal Mode
```bash
docker.bat test
```
- Shows pass/fail results only
- Quick validation
- Clean output

#### 2. Verbose Mode
```bash
docker.bat test-verbose
```
Shows complete request/response logs:
```
=== Testing Async Create Product ===

--- REQUEST ---
mutation {
    createProduct(
        title: "MacBook Pro M3",
        price: 2399.99
    ) {
        success
        message
    }
}

--- RESPONSE ---
Status: 200
{
  "data": {
    "createProduct": {
      "success": true,
      "message": "Product 'MacBook Pro M3' queued for creation"
    }
  }
}
```

#### 3. Debug Mode
```bash
docker.bat test-debug
```
- All verbose output
- Server logs (last 50 lines)
- Complete debugging information

### Test Coverage

- Health check endpoint
- Async product creation
- Sync product creation
- Product queries with all fields
- Product updates (async)
- Search functionality
- Pagination with skip

## Project Structure

```
├── app.py                 # Main Flask application with GraphQL schema
├── async_db.py           # Async database operations (fire-and-forget writes)
├── integration_test.py   # Integration tests with verbose logging
├── init_db.py           # Database initialization with sample data
├── docker-compose.yml    # Docker orchestration
├── Dockerfile           # Container definition
├── requirements.txt     # Python dependencies
├── docker.bat          # Windows helper script
├── docker.sh           # Linux/Mac helper script
└── product_types.py    # Type definitions
```

### Async Write Operations

The system uses a task queue pattern for write operations:

1. **Request arrives** → GraphQL mutation
2. **Queue write operation** → Returns success immediately
3. **Background thread** → Processes write asynchronously
4. **No blocking** → API stays responsive

```python
# Fire-and-forget create
fire_and_forget_create(product_data)
return CreateProduct(success=True, message="Queued for creation")

# Background thread handles actual DB write
async def _async_create(self, product_data):
    async with aiosqlite.connect(self.db_path) as db:
        await db.execute(INSERT_QUERY, data)
        await db.commit()
```

### Synchronous Read Operations

Reads remain synchronous for simplicity and performance:

```python
def resolve_product(self, info, product_id):
    return Product.query.filter_by(id=product_id).first()
```

## Demo Mode

Perfect for demonstrating the system:

```bash
docker.bat demo
```

This command:
1. Starts the application
2. Waits for it to be ready
3. Runs tests with full verbose output
4. Shows all requests and responses
5. Keeps the app running for manual testing

## Technologies Used

- **Flask** 2.2.5 - Web framework
- **GraphQL** (Graphene) - API layer
- **SQLAlchemy** 1.4.48 - ORM
- **SQLite** - Database
- **aiosqlite** - Async database operations
- **Docker** - Containerization
- **pytest** - Testing

## Performance Characteristics

- **Write latency**: ~5ms (returns immediately, processes async)
- **Read latency**: ~10-20ms (direct DB query)

## Development Workflow

### Initial Setup
```bash
# Clone repository
git clone <repo>
cd fusion-python-test

# Make script executable (Linux/Mac)
chmod +x docker.sh

# Start fresh
docker.bat fresh     # Windows
./docker.sh fresh    # Linux/Mac
```

### Development Cycle
```bash
# Start app in background
docker.bat start

# Make code changes...

# Restart to apply changes
docker.bat restart

# Run tests
docker.bat test-verbose

# Check logs if needed
docker.bat logs
```

### Debugging Issues
```bash
# Full reset
docker.bat clean
docker.bat fresh

# Debug with verbose tests
docker.bat test-debug

# Interactive debugging
docker.bat shell
python app.py  # Run manually
```

## Troubleshooting

### Port Already in Use
```bash
# Check what's using port 5000
netstat -ano | findstr :5000    # Windows
lsof -i :5000                    # Linux/Mac

# Or change port in docker-compose.yml
ports:
  - "8000:5000"  # Use port 8000 instead
```

### Container Issues
```bash
# Complete cleanup
docker.bat clean

# Check running containers
docker ps

# Check logs
docker.bat logs
```

### Test Failures
```bash
# Run verbose to see actual responses
docker.bat test-verbose

# Check server logs
docker.bat test-debug
```