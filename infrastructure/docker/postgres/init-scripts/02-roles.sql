-- Application database roles for Row-Level Security

-- Role for tenant-scoped queries (used by application)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'app_tenant_scoped') THEN
        CREATE ROLE app_tenant_scoped NOLOGIN;
    END IF;
END
$$;

-- Role for admin queries (bypasses RLS)
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
