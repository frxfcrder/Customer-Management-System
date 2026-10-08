from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, UniqueConstraint, func
from sqlalchemy.orm import relationship

from .base import Base


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Many-to-many to customers via association table
    customers = relationship("Customer", secondary="category_customers", back_populates="categories")

    # Timestamps (were missing vs models.sql)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class CategoryCustomer(Base):
    __tablename__ = 'category_customers'
    __table_args__ = (
        UniqueConstraint('category_id', 'customer_id', name='uq_category_customers_pair'),
    )

    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)

    # Timestamp (was missing vs models.sql)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# Backwards-compatible aliases (old __init__ imported both spellings)
Category_Customers = CategoryCustomer
Category_Customer = CategoryCustomer
