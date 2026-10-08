import models


def test_models_registered():
    assert models.Customer.__tablename__ == "customers"
    assert models.Order.__tablename__ == "orders"
    assert models.Category.__tablename__ == "categories"
    assert models.CategoryCustomer.__tablename__ == "category_customers"
    # aliases kept for backwards compat
    assert models.Category_Customers is models.CategoryCustomer
    assert models.Category_Customer is models.CategoryCustomer
