# Postman Collection Guide

## Import Instructions

1. Open Postman
2. Click "Import" button (top left)
3. Select the file: `Product_GraphQL_API.postman_collection.json`
4. Click "Import"

## Collection Structure

The collection is organized into folders:

### 1. Health Check
- Simple GET request to verify the server is running

### 2. Queries
- **Get All Products** - Fetch all products with complete data
- **Get Products with Pagination** - Use `first` and `skip` variables
- **Search Products** - Search by title/description
- **Get Product by ID** - Fetch specific product

### 3. Mutations - Async
- **Create Product (Fire & Forget)** - Returns success message only
- **Update Product (Fire & Forget)** - Returns success message only

### 4. Mutations - Sync  
- **Create Product Sync** - Returns product with ID

### 5. Sample Products
Pre-configured mutations to create:
- Gaming Mouse (Razer)
- Gaming Keyboard (Corsair)
- Office Chair (Herman Miller)
- iPhone 15 Pro Max

## How to Use

### Basic Testing Flow

1. **Start the API**
   ```bash
   docker.bat start
   ```

2. **Import Collection** into Postman

3. **Test Health Check**
   - Run "Health Status" request
   - Should return `{"status": "ok"}`

4. **Create Sample Data**
   - Run requests in "Sample Products" folder
   - These create realistic test products

5. **Query Products**
   - Run "Get All Products" to see everything
   - Try "Search Products" with different search terms
   - Test pagination with different `first` and `skip` values

### Variables

The collection uses a variable for the base URL:
- `baseUrl`: Default is `http://localhost:5000`

To change it:
1. Click collection settings (...)
2. Edit > Variables tab
3. Update `baseUrl` value

### GraphQL Variables

Many requests use GraphQL variables for flexibility. Example:

```json
{
  "productId": 1,
  "title": "New Title",
  "price": 99.99
}
```

You can modify these in the "GraphQL Variables" section of each request.

### Automated Tests

Each request includes basic tests:
- Status code is 200
- Response has data field
- No GraphQL errors

Results appear in the "Test Results" tab after running a request.

## Testing Async Architecture

To see the async fire-and-forget pattern:

1. **Run Async Create**
   - Check response: Only `success` and `message` fields
   - No product ID returned

2. **Wait 1-2 seconds**

3. **Run Get All Products**
   - Verify the product appears

4. **Compare with Sync Create**
   - Returns full product with ID immediately
   - Use when you need the ID for subsequent operations

## Sample Workflow

```
1. Health Check → Verify server is up
2. Create Product (Async) → Fire and forget
3. Create Product (Sync) → Get ID back
4. Get All Products → See all data
5. Search "Gaming" → Find gaming products
6. Update Product (Async) → Fire and forget update
7. Get Product by ID → Verify update
```

## Tips

- Use **Ctrl+Enter** to run current request
- Click **"Save"** after modifying variables
- Use **"Duplicate"** to create variations of requests
- Check **"Console"** (bottom left) for detailed logs
- Enable **"Retain headers"** for consistent testing

## Troubleshooting

### Connection Refused
- Ensure Docker container is running: `docker.bat start`
- Check if port 5000 is available
- Verify `baseUrl` variable is correct

### No Data in Response
- Check GraphQL syntax in request body
- Verify variables are properly formatted JSON
- Look for errors in the response

### Async Operations Not Appearing
- Wait 1-2 seconds after async operations
- Refresh by running "Get All Products" again
