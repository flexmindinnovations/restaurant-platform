-- Row-Level Security configuration templates and helpers

-- Helper function to retrieve the current restaurant ID from the session config
CREATE OR REPLACE FUNCTION get_current_restaurant_id() RETURNS text AS $$
BEGIN
    RETURN current_setting('app.current_restaurant_id', true);
END;
$$ LANGUAGE plpgsql STABLE;


-- Stored procedure to automatically enable RLS and apply tenant isolation
CREATE OR REPLACE PROCEDURE enable_tenant_rls(
    table_schema text,
    table_name text,
    tenant_column text DEFAULT 'restaurant_id'
) AS $$
BEGIN
    -- Enable RLS
    EXECUTE format('ALTER TABLE %I.%I ENABLE ROW LEVEL SECURITY', table_schema, table_name);

    -- Force RLS (applies to owner as well)
    EXECUTE format('ALTER TABLE %I.%I FORCE ROW LEVEL SECURITY', table_schema, table_name);

    -- Drop policy if it already exists
    EXECUTE format('DROP POLICY IF EXISTS tenant_isolation_policy ON %I.%I', table_schema, table_name);

    -- Create tenant isolation policy
    EXECUTE format(
        'CREATE POLICY tenant_isolation_policy ON %I.%I AS RESTRICTIVE USING (%I = get_current_restaurant_id()::uuid)',
        table_schema,
        table_name,
        tenant_column
    );
END;
$$ LANGUAGE plpgsql;
