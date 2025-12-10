-- =====================================================
-- EKKLESIA TENANT DATABASE SCHEMA
-- Esquema completo para cada iglesia
-- =====================================================

-- =====================================================
-- TIPOS ENUM
-- =====================================================
DO $$ BEGIN
    CREATE TYPE user_role AS ENUM ('public', 'member', 'admin');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE donation_type AS ENUM ('diezmo', 'ofrenda', 'misiones', 'especial');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE payment_method AS ENUM ('efectivo', 'transferencia', 'tarjeta', 'otro');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- =====================================================
-- CONFIGURACIÓN DE LA IGLESIA
-- =====================================================
CREATE TABLE IF NOT EXISTS church_config (
    id SERIAL PRIMARY KEY,
    church_name VARCHAR(255) NOT NULL DEFAULT 'Mi Iglesia',
    slogan VARCHAR(500),
    description TEXT,
    about_us TEXT,
    mission TEXT,
    vision TEXT,
    "values" TEXT,
    history TEXT,
    
    -- Contacto
    address TEXT,
    city VARCHAR(100),
    country VARCHAR(100),
    phone VARCHAR(50),
    email VARCHAR(255),
    website VARCHAR(255),
    
    -- Branding
    logo_url VARCHAR(500),
    cover_image_url VARCHAR(500),
    primary_color VARCHAR(7) DEFAULT '#8b5cf6',
    secondary_color VARCHAR(7) DEFAULT '#06b6d4',
    
    -- Redes sociales
    social_facebook VARCHAR(255),
    social_instagram VARCHAR(255),
    social_youtube VARCHAR(255),
    social_twitter VARCHAR(255),
    social_tiktok VARCHAR(255),
    
    -- Donaciones
    donation_info TEXT,
    bank_info JSONB,
    paypal_email VARCHAR(255),
    donation_link VARCHAR(500),
    
    -- Horarios
    service_schedule JSONB,
    
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insertar configuración inicial
INSERT INTO church_config (church_name) VALUES ('Mi Iglesia') ON CONFLICT DO NOTHING;

-- =====================================================
-- USUARIOS
-- =====================================================
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role user_role DEFAULT 'member',
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Perfil extendido
    phone VARCHAR(50),
    address TEXT,
    birth_date DATE,
    profile_image_url VARCHAR(500),
    
    -- Preferencias
    notifications_enabled BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- =====================================================
-- EVENTOS
-- =====================================================
CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    start_date DATE,
    end_date DATE,
    start_time TIME,
    end_time TIME,
    location VARCHAR(255),
    capacity INTEGER,
    is_public BOOLEAN DEFAULT TRUE,
    is_featured BOOLEAN DEFAULT FALSE,
    image_url VARCHAR(500),
    created_by_id INTEGER REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_events_dates ON events(start_date, end_date);
CREATE INDEX IF NOT EXISTS idx_events_public ON events(is_public);

-- =====================================================
-- DONACIONES (Formato actualizado con montos separados)
-- =====================================================
CREATE TABLE IF NOT EXISTS donations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    event_id INTEGER REFERENCES events(id),
    
    -- Datos del donante
    donor_name VARCHAR(255) NOT NULL,
    donor_document VARCHAR(50),
    donor_address VARCHAR(500),
    donor_phone VARCHAR(50),
    donor_email VARCHAR(255),
    
    -- Montos separados por tipo
    amount_tithe NUMERIC(12,2) DEFAULT 0,
    amount_offering NUMERIC(12,2) DEFAULT 0,
    amount_missions NUMERIC(12,2) DEFAULT 0,
    amount_special NUMERIC(12,2) DEFAULT 0,
    amount_total NUMERIC(12,2) NOT NULL,
    
    -- Método de pago
    is_cash BOOLEAN DEFAULT TRUE,
    is_transfer BOOLEAN DEFAULT FALSE,
    payment_reference VARCHAR(100),
    
    -- Metadatos
    donation_date DATE NOT NULL,
    week_number INTEGER,
    envelope_number VARCHAR(50),
    note TEXT,
    receipt_number VARCHAR(50) UNIQUE,
    
    -- Auditoría
    is_anonymous BOOLEAN DEFAULT FALSE,
    created_by_id INTEGER REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_donations_user ON donations(user_id);
CREATE INDEX IF NOT EXISTS idx_donations_date ON donations(donation_date);
CREATE INDEX IF NOT EXISTS idx_donations_week ON donations(week_number);

-- =====================================================
-- RESUMEN DE DONACIONES (Para reportes a contaduría)
-- =====================================================
CREATE TABLE IF NOT EXISTS donation_summaries (
    id SERIAL PRIMARY KEY,
    summary_date DATE NOT NULL,
    week_number INTEGER NOT NULL,
    year INTEGER NOT NULL,
    envelope_count INTEGER DEFAULT 0,
    
    -- Totales por tipo y método
    tithe_cash NUMERIC(12,2) DEFAULT 0,
    tithe_transfer NUMERIC(12,2) DEFAULT 0,
    offering_cash NUMERIC(12,2) DEFAULT 0,
    offering_transfer NUMERIC(12,2) DEFAULT 0,
    missions_cash NUMERIC(12,2) DEFAULT 0,
    missions_transfer NUMERIC(12,2) DEFAULT 0,
    special_cash NUMERIC(12,2) DEFAULT 0,
    special_transfer NUMERIC(12,2) DEFAULT 0,
    
    -- Totales generales
    total_cash NUMERIC(12,2) DEFAULT 0,
    total_transfer NUMERIC(12,2) DEFAULT 0,
    grand_total NUMERIC(12,2) DEFAULT 0,
    
    -- Diezmo de diezmos
    tithe_of_tithes NUMERIC(12,2) DEFAULT 0,
    
    -- Testigos
    witness_1_name VARCHAR(255),
    witness_1_document VARCHAR(50),
    witness_2_name VARCHAR(255),
    witness_2_document VARCHAR(50),
    
    -- Auditoría
    created_by_id INTEGER REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    is_closed BOOLEAN DEFAULT FALSE,
    closed_at TIMESTAMPTZ,
    notes TEXT,
    
    UNIQUE(year, week_number)
);

CREATE INDEX IF NOT EXISTS idx_summaries_date ON donation_summaries(summary_date);
CREATE INDEX IF NOT EXISTS idx_summaries_week ON donation_summaries(year, week_number);

-- =====================================================
-- DOCUMENTOS
-- =====================================================
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    stored_path VARCHAR(500) NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    size_bytes INTEGER NOT NULL,
    checksum VARCHAR(64),
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    donation_id INTEGER REFERENCES donations(id),
    user_id INTEGER REFERENCES users(id),
    event_id INTEGER REFERENCES events(id),
    uploaded_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_documents_user ON documents(user_id);
CREATE INDEX IF NOT EXISTS idx_documents_donation ON documents(donation_id);

-- =====================================================
-- INSCRIPCIONES A EVENTOS
-- =====================================================
CREATE TABLE IF NOT EXISTS registrations (
    id SERIAL PRIMARY KEY,
    event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id),
    attendee_name VARCHAR(255) NOT NULL,
    attendee_email VARCHAR(255) NOT NULL,
    attendee_phone VARCHAR(50),
    notes TEXT,
    is_cancelled BOOLEAN DEFAULT FALSE,
    checked_in BOOLEAN DEFAULT FALSE,
    checked_in_at TIMESTAMPTZ,
    registered_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_registrations_event ON registrations(event_id);
CREATE INDEX IF NOT EXISTS idx_registrations_email ON registrations(attendee_email);
CREATE UNIQUE INDEX IF NOT EXISTS idx_registrations_unique 
    ON registrations(event_id, attendee_email) WHERE NOT is_cancelled;

-- =====================================================
-- TRANSMISIONES EN VIVO
-- =====================================================
CREATE TABLE IF NOT EXISTS live_streams (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    stream_url VARCHAR(500),
    youtube_video_id VARCHAR(50),
    facebook_video_id VARCHAR(100),
    platform VARCHAR(50) DEFAULT 'youtube',
    is_live BOOLEAN DEFAULT FALSE,
    is_featured BOOLEAN DEFAULT FALSE,
    scheduled_at TIMESTAMPTZ,
    started_at TIMESTAMPTZ,
    ended_at TIMESTAMPTZ,
    thumbnail_url VARCHAR(500),
    view_count INTEGER DEFAULT 0,
    created_by_id INTEGER REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_streams_live ON live_streams(is_live);
CREATE INDEX IF NOT EXISTS idx_streams_scheduled ON live_streams(scheduled_at);

-- =====================================================
-- CONTENIDO PÚBLICO
-- =====================================================
CREATE TABLE IF NOT EXISTS public_content (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    excerpt VARCHAR(500),
    content_type VARCHAR(50) DEFAULT 'page',
    featured_image_url VARCHAR(500),
    is_published BOOLEAN DEFAULT TRUE,
    is_featured BOOLEAN DEFAULT FALSE,
    published_at TIMESTAMPTZ,
    meta_title VARCHAR(255),
    meta_description VARCHAR(500),
    created_by_id INTEGER REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_content_slug ON public_content(slug);
CREATE INDEX IF NOT EXISTS idx_content_published ON public_content(is_published);

-- =====================================================
-- ANUNCIOS
-- =====================================================
CREATE TABLE IF NOT EXISTS announcements (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    announcement_type VARCHAR(50) DEFAULT 'general',
    priority INTEGER DEFAULT 0,
    is_public BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE,
    start_date TIMESTAMPTZ,
    end_date TIMESTAMPTZ,
    created_by_id INTEGER REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_announcements_active ON announcements(is_active);
CREATE INDEX IF NOT EXISTS idx_announcements_dates ON announcements(start_date, end_date);

-- =====================================================
-- MINISTERIOS / GRUPOS
-- =====================================================
CREATE TABLE IF NOT EXISTS ministries (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    leader_id INTEGER REFERENCES users(id),
    meeting_schedule JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    image_url VARCHAR(500),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Miembros de ministerios
CREATE TABLE IF NOT EXISTS ministry_members (
    id SERIAL PRIMARY KEY,
    ministry_id INTEGER REFERENCES ministries(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'member',
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(ministry_id, user_id)
);

-- =====================================================
-- PETICIONES DE ORACIÓN
-- =====================================================
CREATE TABLE IF NOT EXISTS prayer_requests (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    requester_name VARCHAR(255),
    request_text TEXT NOT NULL,
    is_public BOOLEAN DEFAULT FALSE,
    is_answered BOOLEAN DEFAULT FALSE,
    prayer_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_prayers_public ON prayer_requests(is_public);

-- =====================================================
-- CATEGORÍAS DE GASTOS
-- =====================================================
CREATE TABLE IF NOT EXISTS expense_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    color VARCHAR(7) DEFAULT '#6b7280',
    icon VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    monthly_budget NUMERIC(12,2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Categorías predeterminadas
INSERT INTO expense_categories (name, description, color, icon, sort_order) VALUES
('Servicios Públicos', 'Agua, luz, gas, internet, teléfono', '#3b82f6', 'ri-lightbulb-line', 1),
('Arriendo', 'Alquiler del local o instalaciones', '#8b5cf6', 'ri-home-line', 2),
('Salarios', 'Pagos a personal y colaboradores', '#22c55e', 'ri-user-line', 3),
('Mantenimiento', 'Reparaciones y mantenimiento de instalaciones', '#f59e0b', 'ri-tools-line', 4),
('Suministros', 'Materiales de oficina, limpieza, etc.', '#06b6d4', 'ri-shopping-bag-line', 5),
('Eventos', 'Gastos relacionados con eventos especiales', '#ec4899', 'ri-calendar-event-line', 6),
('Transporte', 'Combustible, pasajes, viáticos', '#84cc16', 'ri-car-line', 7),
('Misiones', 'Apoyo a misiones y evangelismo', '#f97316', 'ri-earth-line', 8),
('Otros', 'Gastos varios no clasificados', '#6b7280', 'ri-more-line', 99)
ON CONFLICT DO NOTHING;

-- =====================================================
-- SUBCATEGORÍAS DE GASTOS
-- =====================================================
CREATE TABLE IF NOT EXISTS expense_subcategories (
    id SERIAL PRIMARY KEY,
    category_id INTEGER NOT NULL REFERENCES expense_categories(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_subcategories_category ON expense_subcategories(category_id);

-- Subcategorías predeterminadas
INSERT INTO expense_subcategories (category_id, name) VALUES
(1, 'Energía Eléctrica'),
(1, 'Agua'),
(1, 'Gas'),
(1, 'Internet'),
(1, 'Teléfono'),
(3, 'Pastor'),
(3, 'Secretaria'),
(3, 'Personal de limpieza'),
(4, 'Plomería'),
(4, 'Electricidad'),
(4, 'Pintura'),
(4, 'Carpintería')
ON CONFLICT DO NOTHING;

-- =====================================================
-- ETIQUETAS DE GASTOS
-- =====================================================
CREATE TABLE IF NOT EXISTS expense_tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    color VARCHAR(7) DEFAULT '#3b82f6',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO expense_tags (name, color) VALUES
('Urgente', '#ef4444'),
('Recurrente', '#8b5cf6'),
('Deducible', '#22c55e'),
('Pendiente aprobación', '#f59e0b')
ON CONFLICT DO NOTHING;

-- =====================================================
-- GASTOS
-- =====================================================
CREATE TABLE IF NOT EXISTS expenses (
    id SERIAL PRIMARY KEY,
    category_id INTEGER NOT NULL REFERENCES expense_categories(id),
    subcategory_id INTEGER REFERENCES expense_subcategories(id),
    
    description VARCHAR(500) NOT NULL,
    amount NUMERIC(12,2) NOT NULL,
    expense_date DATE NOT NULL,
    
    -- Proveedor
    vendor_name VARCHAR(255),
    vendor_document VARCHAR(50),
    vendor_phone VARCHAR(50),
    
    -- Pago
    payment_method VARCHAR(50) DEFAULT 'efectivo',
    payment_reference VARCHAR(100),
    bank_account VARCHAR(100),
    
    -- Documentos
    invoice_number VARCHAR(50),
    receipt_number VARCHAR(50),
    
    -- Estado
    status VARCHAR(20) DEFAULT 'pending',
    is_recurring BOOLEAN DEFAULT FALSE,
    recurrence_period VARCHAR(20),
    
    tags JSONB,
    notes TEXT,
    
    -- Auditoría
    created_by_id INTEGER NOT NULL REFERENCES users(id),
    approved_by_id INTEGER REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    approved_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_expenses_category ON expenses(category_id);
CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(expense_date);
CREATE INDEX IF NOT EXISTS idx_expenses_status ON expenses(status);
CREATE INDEX IF NOT EXISTS idx_expenses_created_by ON expenses(created_by_id);

-- =====================================================
-- DOCUMENTOS DE GASTOS
-- =====================================================
CREATE TABLE IF NOT EXISTS expense_documents (
    id SERIAL PRIMARY KEY,
    expense_id INTEGER NOT NULL REFERENCES expenses(id) ON DELETE CASCADE,
    
    file_name VARCHAR(255) NOT NULL,
    stored_path VARCHAR(500) NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    size_bytes INTEGER NOT NULL,
    checksum VARCHAR(64),
    
    document_type VARCHAR(50) DEFAULT 'invoice',
    description TEXT,
    
    uploaded_by_id INTEGER REFERENCES users(id),
    uploaded_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_expense_docs_expense ON expense_documents(expense_id);

-- =====================================================
-- CARPETAS DE GASTOS
-- =====================================================
CREATE TABLE IF NOT EXISTS expense_folders (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    parent_id INTEGER REFERENCES expense_folders(id),
    folder_type VARCHAR(50) DEFAULT 'general',
    year INTEGER,
    month INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_folders_parent ON expense_folders(parent_id);

