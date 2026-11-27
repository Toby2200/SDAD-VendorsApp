-- 002: a client can be deactivated instead of deleted, because its old orders still point to it.
-- NOT NULL with a DEFAULT: SQL Server fills every existing row with 1, so no client disappears.
ALTER TABLE clients ADD active BIT NOT NULL CONSTRAINT df_clients_active DEFAULT 1;