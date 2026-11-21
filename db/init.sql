IF DB_ID('catalog_db') IS NULL CREATE DATABASE catalog_db;
GO
IF DB_ID('sales_db') IS NULL CREATE DATABASE sales_db;
GO

IF SUSER_ID('catalog_user') IS NULL
    CREATE LOGIN catalog_user WITH PASSWORD = '$(CATALOG_DB_PASSWORD)';
GO
IF SUSER_ID('sales_user') IS NULL
    CREATE LOGIN sales_user WITH PASSWORD = '$(SALES_DB_PASSWORD)';
GO

USE catalog_db;
GO
IF USER_ID('catalog_user') IS NULL
BEGIN
    CREATE USER catalog_user FOR LOGIN catalog_user;
    ALTER ROLE db_owner ADD MEMBER catalog_user;
END
GO

USE sales_db;
GO
IF USER_ID('sales_user') IS NULL
BEGIN
    CREATE USER sales_user FOR LOGIN sales_user;
    ALTER ROLE db_owner ADD MEMBER sales_user;
END
GO