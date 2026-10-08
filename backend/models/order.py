from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from .base import Base


class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id', ondelete='CASCADE'), nullable=False, index=True)

    # Fields (Numeric for money — avoids float rounding in a sellable product)
    total_amount = Column(Numeric(10, 2), default=0.00, index=True)
    status = Column(String(50), default="pending", nullable=False)  # "pending", "completed", "cancelled"

    payment_status = Column(String(50), default="unpaid")

    customer = relationship("Customer", back_populates="orders")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
