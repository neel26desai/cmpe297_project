from fastapi import FastAPI, Query, Path, Body, HTTPException

app = FastAPI()

# Basic GET endpoint
@app.get("/hello")
def say_hello(name: str = "World"):
    """
    Say hello to the user.
    """
    return {"message": f"Hello, {name}!"}

# GET endpoint with path and query parameters
@app.get("/items/{item_id}")
def get_item(
    item_id: int = Path(..., description="The ID of the item"),
    details: bool = Query(False, description="Include detailed information")
):
    """
    Fetch details of an item.
    """
    if item_id > 1000:
        raise HTTPException(status_code=404, detail="Item not found")
    if details:
        return {"item_id": item_id, "name": "Sample Item", "details": "This is a detailed description."}
    return {"item_id": item_id, "name": "Sample Item"}

# POST endpoint to create an item
@app.post("/items/")
def create_item(
    item: dict = Body(..., description="The item to create")
):
    """
    Create a new item.
    """
    return {"message": "Item created successfully", "item": item}

# PUT endpoint to update an item
@app.put("/items/{item_id}")
def update_item(
    item_id: int = Path(..., description="The ID of the item to update"),
    item: dict = Body(..., description="The new item data")
):
    """
    Update an existing item.
    """
    return {"message": f"Item {item_id} updated successfully", "item": item}

# DELETE endpoint to delete an item
@app.delete("/items/{item_id}")
def delete_item(item_id: int = Path(..., description="The ID of the item to delete")):
    """
    Delete an item.
    """
    return {"message": f"Item {item_id} deleted successfully"}

# Advanced GET endpoint with filtering and sorting
@app.get("/products/")
def list_products(
    category: str = Query(None, description="Filter by product category"),
    price_min: float = Query(0.0, description="Minimum price"),
    price_max: float = Query(10000.0, description="Maximum price"),
    sort_by: str = Query("name", description="Sort by field (name or price)")
):
    """
    List products with optional filtering and sorting.
    """
    products = [
        {"id": 1, "name": "Product A", "price": 50.0, "category": "Electronics"},
        {"id": 2, "name": "Product B", "price": 30.0, "category": "Books"},
        {"id": 3, "name": "Product C", "price": 20.0, "category": "Electronics"}
    ]
    # Filter by category
    if category:
        products = [p for p in products if p["category"] == category]
    # Filter by price range
    products = [p for p in products if price_min <= p["price"] <= price_max]
    # Sort by field
    products = sorted(products, key=lambda x: x[sort_by])
    return {"products": products}

# Endpoint to demonstrate validation errors
@app.post("/register/")
def register_user(
    username: str = Body(..., min_length=3, max_length=50, description="The username of the user"),
    password: str = Body(..., min_length=6, description="The password of the user")
):
    """
    Register a new user.
    """
    if username == "admin":
        raise HTTPException(status_code=400, detail="Username 'admin' is not allowed.")
    return {"message": f"User {username} registered successfully."}

# Health check endpoint
@app.get("/health/")
def health_check():
    """
    Check the health of the API.
    """
    return {"status": "OK"}
