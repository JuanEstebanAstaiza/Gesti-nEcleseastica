-- =====================================================
-- EKKLESIA MASTER DATABASE SCHEMA
-- Base de datos principal para gestión de tenants
-- =====================================================

-- Extensión para UUID
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =====================================================
-- PLANES DE SUSCRIPCIÓN
-- =====================================================
CREATE TABLE IF NOT EXISTS subscription_plans (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    max_users INTEGER,
    max_storage_mb INTEGER,
    features JSONB,
    price_monthly NUMERIC(10,2),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Planes iniciales
INSERT INTO subscription_plans (name, description, max_users, max_storage_mb, features, price_monthly) VALUES
('Gratuito', 'Plan básico gratuito', 50, 500, '{"donations": true, "events": true, "documents": true, "streaming": false}', 0),
('Básico', 'Plan para iglesias pequeñas', 200, 2000, '{"donations": true, "events": true, "documents": true, "streaming": true}', 29.99),
('Profesional', 'Plan completo para iglesias medianas', 1000, 10000, '{"donations": true, "events": true, "documents": true, "streaming": true, "analytics": true}', 79.99),
('Empresarial', 'Plan ilimitado', NULL, NULL, '{"donations": true, "events": true, "documents": true, "streaming": true, "analytics": true, "api_access": true}', 199.99)
ON CONFLICT DO NOTHING;

-- =====================================================
-- TENANTS (IGLESIAS)
-- =====================================================
CREATE TABLE IF NOT EXISTS tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    subdomain VARCHAR(100) UNIQUE,
    custom_domain VARCHAR(255),
    db_name VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    plan_id INTEGER REFERENCES subscription_plans(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_tenants_slug ON tenants(slug);
CREATE INDEX IF NOT EXISTS idx_tenants_subdomain ON tenants(subdomain);
CREATE INDEX IF NOT EXISTS idx_tenants_is_active ON tenants(is_active);

-- =====================================================
-- SUPER ADMINISTRADORES
-- =====================================================
CREATE TABLE IF NOT EXISTS super_admins (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_super_admins_email ON super_admins(email);

-- =====================================================
-- ADMINISTRADORES DE TENANT (referencia)
-- =====================================================
CREATE TABLE IF NOT EXISTS tenant_admins (
    id SERIAL PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tenant_admins_tenant_id ON tenant_admins(tenant_id);

-- =====================================================
-- LOGS DE ACTIVIDAD
-- =====================================================
CREATE TABLE IF NOT EXISTS activity_logs (
    id SERIAL PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    super_admin_id INTEGER REFERENCES super_admins(id),
    action VARCHAR(100) NOT NULL,
    details JSONB,
    ip_address VARCHAR(45),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_activity_logs_tenant ON activity_logs(tenant_id);
CREATE INDEX IF NOT EXISTS idx_activity_logs_date ON activity_logs(created_at);

-- =====================================================
-- DATOS INICIALES
-- =====================================================

-- Super Admin (contraseña: superadmin123)
INSERT INTO super_admins (email, hashed_password, full_name) VALUES
('super@ekklesia.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4e0TdMJ.jx.12b/W', 'Super Administrador')
ON CONFLICT (email) DO NOTHING;

-- Tenant demo (Iglesia Comunidad de Fe)
INSERT INTO tenants (slug, name, subdomain, db_name, plan_id) VALUES
('comunidad-de-fe', 'Iglesia Comunidad de Fe', 'comunidadfe', 'ekklesia', 2)
ON CONFLICT (slug) DO NOTHING;

