-- Application database roles for Row-Level Security

-- Role for tenant-scoped queries (used by application)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'app_tenant_scoped') THEN
        CREATE ROLE app_tenant_scoped NOLOGIN;
    END IF;
END
$$;

-- Role for admin/migration queries (bypasses RLS)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'app_admin') THEN
        CREATE ROLE app_admin NOLOGIN;
    END IF;
END
$$;

-- Grant roles to application user
GRANT app_tenant_scoped TO platform;
GRANT app_admin TO platform;

-- Grant usage on schemas to application roles
GRANT USAGE ON SCHEMA identity TO app_tenant_scoped, app_admin;
GRANT USAGE ON SCHEMA users TO app_tenant_scoped, app_admin;
GRANT USAGE ON SCHEMA restaurants TO app_tenant_scoped, app_admin;
GRANT USAGE ON SCHEMA menus TO app_tenant_scoped, app_admin;
GRANT USAGE ON SCHEMA orders TO app_tenant_scoped, app_admin;
GRANT USAGE ON SCHEMA payments TO app_tenant_scoped, app_admin;
GRANT USAGE ON SCHEMA deliveries TO app_tenant_scoped, app_admin;
GRANT USAGE ON SCHEMA notifications TO app_tenant_scoped, app_admin;
GRANT USAGE ON SCHEMA reviews TO app_tenant_scoped, app_admin;
GRANT USAGE ON SCHEMA promotions TO app_tenant_scoped, app_admin;
GRANT USAGE ON SCHEMA analytics TO app_tenant_scoped, app_admin;

-- Set default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA identity GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_tenant_scoped;
ALTER DEFAULT PRIVILEGES IN SCHEMA users GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_tenant_scoped;
ALTER DEFAULT PRIVILEGES IN SCHEMA restaurants GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_tenant_scoped;
ALTER DEFAULT PRIVILEGES IN SCHEMA menus GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_tenant_scoped;
ALTER DEFAULT PRIVILEGES IN SCHEMA orders GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_tenant_scoped;
ALTER DEFAULT PRIVILEGES IN SCHEMA payments GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_tenant_scoped;
ALTER DEFAULT PRIVILEGES IN SCHEMA deliveries GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_tenant_scoped;
ALTER DEFAULT PRIVILEGES IN SCHEMA notifications GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_tenant_scoped;
ALTER DEFAULT PRIVILEGES IN SCHEMA reviews GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_tenant_scoped;
ALTER DEFAULT PRIVILEGES IN SCHEMA promotions GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_tenant_scoped;
ALTER DEFAULT PRIVILEGES IN SCHEMA analytics GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_tenant_scoped;

ALTER DEFAULT PRIVILEGES IN SCHEMA identity GRANT ALL PRIVILEGES ON TABLES TO app_admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA users GRANT ALL PRIVILEGES ON TABLES TO app_admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA restaurants GRANT ALL PRIVILEGES ON TABLES TO app_admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA menus GRANT ALL PRIVILEGES ON TABLES TO app_admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA orders GRANT ALL PRIVILEGES ON TABLES TO app_admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA payments GRANT ALL PRIVILEGES ON TABLES TO app_admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA deliveries GRANT ALL PRIVILEGES ON TABLES TO app_admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA notifications GRANT ALL PRIVILEGES ON TABLES TO app_admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA reviews GRANT ALL PRIVILEGES ON TABLES TO app_admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA promotions GRANT ALL PRIVILEGES ON TABLES TO app_admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA analytics GRANT ALL PRIVILEGES ON TABLES TO app_admin;
