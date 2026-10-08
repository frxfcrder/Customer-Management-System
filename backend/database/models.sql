-- Customer Management System Migration File
-- Generated: 2026-10-08 (from SQLAlchemy ORM Base.metadata)

-- Table: categories
CREATE TABLE IF NOT EXISTS categories (
	id SERIAL NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	description TEXT, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
	PRIMARY KEY (id)
);

-- Table: customers
CREATE TABLE IF NOT EXISTS customers (
	id SERIAL NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	email VARCHAR(255) NOT NULL, 
	phone VARCHAR(20), 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
	PRIMARY KEY (id)
);

-- Table: category_customers
CREATE TABLE IF NOT EXISTS category_customers (
	id SERIAL NOT NULL, 
	category_id INTEGER NOT NULL, 
	customer_id INTEGER NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
	PRIMARY KEY (id), 
	CONSTRAINT uq_category_customers_pair UNIQUE (category_id, customer_id), 
	FOREIGN KEY(category_id) REFERENCES categories (id) ON DELETE CASCADE, 
	FOREIGN KEY(customer_id) REFERENCES customers (id) ON DELETE CASCADE
);

-- Table: orders
CREATE TABLE IF NOT EXISTS orders (
	id SERIAL NOT NULL, 
	customer_id INTEGER NOT NULL, 
	total_amount NUMERIC(10, 2), 
	status VARCHAR(50) NOT NULL, 
	payment_status VARCHAR(50), 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
	PRIMARY KEY (id), 
	FOREIGN KEY(customer_id) REFERENCES customers (id) ON DELETE CASCADE
);

-- Indexes for performance (from ORM index=True + PK/unique/constraints)
CREATE UNIQUE INDEX IF NOT EXISTS ix_categories_name ON categories (name);
CREATE UNIQUE INDEX IF NOT EXISTS ix_customers_email ON customers (email);
CREATE INDEX IF NOT EXISTS ix_customers_name ON customers (name);
CREATE INDEX IF NOT EXISTS ix_customers_phone ON customers (phone);
CREATE INDEX IF NOT EXISTS ix_category_customers_category_id ON category_customers (category_id);
CREATE INDEX IF NOT EXISTS ix_category_customers_customer_id ON category_customers (customer_id);
CREATE INDEX IF NOT EXISTS ix_orders_total_amount ON orders (total_amount);
CREATE INDEX IF NOT EXISTS ix_orders_customer_id ON orders (customer_id);
