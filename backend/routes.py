from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from models import Category, Customer, Order
from schemas import CustomerCreate, CustomerUpdate, LoginRequest, OrderStatusUpdate
from services.auth import AuthService
from services.db import get_db

auth_service = AuthService()
router = APIRouter(prefix="/api")

require_auth = Depends(auth_service.get_current_user)


@router.get("/health")
def api_health():
    return {"status": "ok"}


# Authentication
@router.post("/auth/login")
def login(credentials: LoginRequest):
    """Login endpoint: returns a JWT on success."""
    ok, message = auth_service.authenticate_user(credentials.email, credentials.password)
    if not ok:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=message)
    return auth_service.generate_token(credentials.email)


# Customers
@router.post("/customers/create", dependencies=[require_auth], status_code=201)
@router.post("/customers", dependencies=[require_auth], status_code=201)
def create_customer(data: CustomerCreate, db: Session = Depends(get_db)):
    """Create a new customer."""
    if db.query(Customer).filter(Customer.email == data.email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already in use")

    customer = Customer(name=data.name, email=data.email, phone=data.phone)
    try:
        db.add(customer)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    db.refresh(customer)
    return customer.to_dict()


@router.post("/customers/{customer_id}", dependencies=[require_auth])
def update_customer(customer_id: int, data: CustomerUpdate, db: Session = Depends(get_db)):
    """Update an existing customer."""
    customer = db.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(customer, field, value)
    db.commit()
    db.refresh(customer)
    return customer.to_dict()


@router.get("/customers/{customer_id}")
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    """Retrieve a single customer by ID."""
    customer = db.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return customer.to_dict()


@router.get("/customers")
def get_customers(page: int = 1, page_size: int = 10, db: Session = Depends(get_db)):
    """Retrieve all customers with filtering and pagination."""
    page = max(page, 1)
    page_size = min(max(page_size, 1), 100)

    query = db.query(Customer)
    total_count = query.count()
    customers = query.order_by(Customer.id).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "data": [c.to_dict() for c in customers],
        "total_count": total_count,
        "page": page,
        "size": page_size,
    }


@router.get("/customers/{customer_id}/orders")
def get_customer_orders(customer_id: int, db: Session = Depends(get_db)):
    """Get all orders for a specific customer."""
    if not db.get(Customer, customer_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

    orders = db.query(Order).filter(Order.customer_id == customer_id).all()
    return {
        "orders": [o.to_dict() for o in orders],
        "count": len(orders),
    }


# Categories
@router.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    """Get all categories."""
    categories = db.query(Category).all()
    return {
        "categories": [c.to_dict() for c in categories],
        "count": len(categories),
    }


@router.get("/categories/{category_id}")
def get_category(category_id: int, db: Session = Depends(get_db)):
    """Get a specific category."""
    category = db.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return category.to_dict()


# Orders
@router.get("/orders")
def list_orders(
    status: str | None = None,
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
):
    """Get all orders with optional status filter and pagination."""
    page = max(page, 1)
    page_size = min(max(page_size, 1), 100)

    query = db.query(Order)
    if status:
        query = query.filter(Order.status == status)

    total_count = query.count()
    orders = (
        query.order_by(Order.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "orders": [o.to_dict() for o in orders],
        "total_count": total_count,
        "page": page,
        "page_size": page_size,
    }


@router.post("/orders/{order_id}", dependencies=[require_auth])
def update_order_status(order_id: int, data: OrderStatusUpdate, db: Session = Depends(get_db)):
    """Update order status."""
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    order.status = data.status
    db.commit()
    return {"message": "Order updated successfully", "order": order.to_dict()}


@router.get("/orders/{order_id}")
def get_order_details(order_id: int, db: Session = Depends(get_db)):
    """Get specific order details."""
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return order.to_dict()
