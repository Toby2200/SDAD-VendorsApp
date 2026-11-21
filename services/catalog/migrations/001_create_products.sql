CREATE TABLE products (
    id_product INT IDENTITY(1, 1) PRIMARY KEY,
    code NVARCHAR(50) NOT NULL UNIQUE,
    description NVARCHAR(255) NOT NULL,
    quantity INT NOT NULL DEFAULT 0,
    active BIT NOT NULL DEFAULT 1,
    price DECIMAL(10, 2) NOT NULL,
    CONSTRAINT ck_products_quantity_not_negative CHECK (quantity >= 0)
);