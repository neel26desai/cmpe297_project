from fastapi import FastAPI, Query, Path, Body, HTTPException, Header, UploadFile, File, Depends
from typing import List, Optional

app = FastAPI()

# Authentication dependency
def authenticate_user(api_key: str = Header(..., description="API Key for authentication")):
    if api_key != "valid_api_key":
        raise HTTPException(status_code=401, detail="Invalid API Key")

# GET endpoint with authentication and pagination
@app.get("/users/", dependencies=[Depends(authenticate_user)])
def list_users(
    page: int = Query(1, description="Page number (1-indexed)"),
    page_size: int = Query(10, description="Number of users per page")
):
    """
    Retrieve a paginated list of users.
    """
    total_users = 50
    if page < 1 or page_size < 1:
        raise HTTPException(status_code=400, detail="Page and page size must be positive integers")
    start = (page - 1) * page_size
    end = start + page_size
    users = [{"id": i, "name": f"User {i}"} for i in range(1, total_users + 1)]
    return {"total": total_users, "users": users[start:end], "page": page, "page_size": page_size}

# POST endpoint with nested JSON body
@app.post("/orders/")
def create_order(
    order: dict = Body(
        ...,
        example={
            "customer_id": 123,
            "items": [{"product_id": 1, "quantity": 2}, {"product_id": 2, "quantity": 1}],
            "total_price": 150.0
        },
        description="Details of the order"
    )
):
    """
    Create a new order with multiple items.
    """
    return {"message": "Order created successfully", "order": order}

# PUT endpoint with file upload and metadata
@app.put("/documents/{doc_id}")
def update_document(
    doc_id: int = Path(..., description="Document ID to update"),
    file: UploadFile = File(..., description="The new document file to upload"),
    metadata: dict = Body(..., description="Metadata for the document")
):
    """
    Update an existing document with a new file and metadata.
    """
    return {
        "message": f"Document {doc_id} updated successfully",
        "file_name": file.filename,
        "metadata": metadata
    }

# GET endpoint with nested filtering and search
@app.get("/products/search/")
def search_products(
    name: Optional[str] = Query(None, description="Search products by name"),
    categories: List[str] = Query([], description="Filter products by categories"),
    in_stock: Optional[bool] = Query(None, description="Filter by in-stock status"),
    min_price: Optional[float] = Query(None, description="Minimum price"),
    max_price: Optional[float] = Query(None, description="Maximum price")
):
    """
    Search for products with advanced filtering options.
    """
    products = [
        {"id": 1, "name": "Laptop", "category": "Electronics", "price": 1000.0, "in_stock": True},
        {"id": 2, "name": "Notebook", "category": "Stationery", "price": 5.0, "in_stock": True},
        {"id": 3, "name": "Smartphone", "category": "Electronics", "price": 500.0, "in_stock": False},
        {"id": 4, "name": "Desk", "category": "Furniture", "price": 150.0, "in_stock": True}
    ]

    if name:
        products = [p for p in products if name.lower() in p["name"].lower()]
    if categories:
        products = [p for p in products if p["category"] in categories]
    if in_stock is not None:
        products = [p for p in products if p["in_stock"] == in_stock]
    if min_price is not None:
        products = [p for p in products if p["price"] >= min_price]
    if max_price is not None:
        products = [p for p in products if p["price"] <= max_price]

    return {"products": products}

# DELETE endpoint with soft delete and status update
@app.delete("/users/{user_id}")
def delete_user(
    user_id: int = Path(..., description="ID of the user to delete"),
    soft_delete: bool = Query(True, description="Perform a soft delete if true")
):
    """
    Delete a user with an option for soft delete.
    """
    if soft_delete:
        return {"message": f"User {user_id} marked as inactive"}
    else:
        return {"message": f"User {user_id} permanently deleted"}

# PATCH endpoint for partial update with validation
@app.patch("/users/{user_id}")
def update_user(
    user_id: int = Path(..., description="ID of the user to update"),
    update_fields: dict = Body(
        ...,
        example={"name": "Updated Name", "email": "new_email@example.com"},
        description="Fields to update"
    )
):
    """
    Partially update user information with validation.
    """
    return {"message": f"User {user_id} updated successfully", "updates": update_fields}
