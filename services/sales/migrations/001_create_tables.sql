CREATE TABLE vendors (
    vendor_id INT IDENTITY(1, 1) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL,
    last_name NVARCHAR(100) NOT NULL,
    mail NVARCHAR(255) NOT NULL UNIQUE,
    password NVARCHAR(255) NOT NULL,
    active BIT NOT NULL DEFAULT 1
);

CREATE TABLE clients (
    client_id INT IDENTITY(1, 1) PRIMARY KEY,
    name NVARCHAR(150) NOT NULL,
    ubicacion NVARCHAR(255) NULL,
    mail NVARCHAR(255) NULL,
    cedula_juridica NVARCHAR(50) NULL,
    vendor_id INT NOT NULL,
    CONSTRAINT fk_clients_vendor FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id)
);

CREATE TABLE orders (
    id_order INT IDENTITY(1, 1) PRIMARY KEY,
    vendor_id INT NOT NULL,
    client_id INT NOT NULL,
    [date] DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT fk_orders_vendor FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id),
    CONSTRAINT fk_orders_client FOREIGN KEY (client_id) REFERENCES clients(client_id)
);

CREATE TABLE orderDetails (
    id_orderDetail INT IDENTITY(1, 1) PRIMARY KEY,
    id_order INT NOT NULL,
    id_product INT NOT NULL, -- ID de un producto de catalog: sin FOREIGN KEY porque está en otra base de datos
    code NVARCHAR(50) NOT NULL,
    description NVARCHAR(255) NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    subtotal DECIMAL(12, 2) NOT NULL,
    CONSTRAINT fk_orderdetails_order FOREIGN KEY (id_order) REFERENCES orders(id_order),
    CONSTRAINT ck_orderdetails_quantity_positive CHECK (quantity > 0)
);