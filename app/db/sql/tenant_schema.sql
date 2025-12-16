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
-- DONACIONES
-- =====================================================
CREATE TABLE IF NOT EXISTS donations (
    id SERIAL PRIMARY KEY,
    donor_name VARCHAR(255) NOT NULL,
    donor_document VARCHAR(50),
    donation_type donation_type NOT NULL,
    user_id INTEGER REFERENCES users(id),
    amount NUMERIC(12,2) NOT NULL,
    payment_method payment_method NOT NULL,
    donation_date DATE NOT NULL,
    note TEXT,
    event_id INTEGER REFERENCES events(id),
    is_anonymous BOOLEAN DEFAULT FALSE,
    receipt_number VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_donations_user ON donations(user_id);
CREATE INDEX IF NOT EXISTS idx_donations_date ON donations(donation_date);
CREATE INDEX IF NOT EXISTS idx_donations_type ON donations(donation_type);

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
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insertar categorías por defecto
INSERT INTO expense_categories (name, description, color) VALUES 
    ('Servicios', 'Agua, luz, internet, etc.', '#3b82f6'),
    ('Mantenimiento', 'Reparaciones y mejoras del templo', '#f59e0b'),
    ('Ministerios', 'Gastos de ministerios y grupos', '#10b981'),
    ('Eventos', 'Gastos de eventos especiales', '#8b5cf6'),
    ('Nómina', 'Salarios y honorarios', '#ef4444'),
    ('Otros', 'Gastos varios', '#6b7280')
ON CONFLICT DO NOTHING;

-- =====================================================
-- GASTOS
-- =====================================================
DO $$ BEGIN
    CREATE TYPE expense_status AS ENUM ('pending', 'approved', 'paid', 'rejected');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

CREATE TABLE IF NOT EXISTS expenses (
    id SERIAL PRIMARY KEY,
    description VARCHAR(255) NOT NULL,
    amount NUMERIC(12,2) NOT NULL,
    category_id INTEGER REFERENCES expense_categories(id),
    expense_date DATE NOT NULL DEFAULT CURRENT_DATE,
    due_date DATE,
    status expense_status DEFAULT 'pending',
    payment_method payment_method,
    receipt_number VARCHAR(50),
    vendor VARCHAR(255),
    notes TEXT,
    document_id INTEGER REFERENCES documents(id),
    created_by_id INTEGER REFERENCES users(id),
    approved_by_id INTEGER REFERENCES users(id),
    approved_at TIMESTAMPTZ,
    paid_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_expenses_status ON expenses(status);
CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(expense_date);
CREATE INDEX IF NOT EXISTS idx_expenses_category ON expenses(category_id);

-- =====================================================
-- RESÚMENES DE DONACIONES (para reportes)
-- =====================================================
CREATE TABLE IF NOT EXISTS donation_summaries (
    id SERIAL PRIMARY KEY,
    period_type VARCHAR(20) NOT NULL, -- 'daily', 'weekly', 'monthly', 'yearly'
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    donation_type donation_type,
    total_amount NUMERIC(14,2) NOT NULL DEFAULT 0,
    transaction_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(period_type, period_start, donation_type)
);

-- Carpetas para gastos (organización)
CREATE TABLE IF NOT EXISTS expense_folders (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    parent_id INTEGER REFERENCES expense_folders(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Subcategorías de gastos
CREATE TABLE IF NOT EXISTS expense_subcategories (
    id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES expense_categories(id),
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Etiquetas para gastos
CREATE TABLE IF NOT EXISTS expense_tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    color VARCHAR(7) DEFAULT '#6b7280',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Documentos de gastos
CREATE TABLE IF NOT EXISTS expense_documents (
    id SERIAL PRIMARY KEY,
    expense_id INTEGER REFERENCES expenses(id) ON DELETE CASCADE,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- DATOS INICIALES
-- =====================================================

-- Configuración de la iglesia
UPDATE church_config SET
    church_name = 'Iglesia Comunidad de Fe',
    slogan = 'Transformando vidas con el amor de Cristo',
    description = 'Somos una comunidad de fe comprometida con el crecimiento espiritual y el servicio.',
    about_us = 'La Iglesia Comunidad de Fe fue fundada en 1995 con la visión de crear un espacio donde las familias pudieran crecer juntas en fe y amor.',
    mission = 'Proclamar el evangelio de Jesucristo, formar discípulos comprometidos y servir a nuestra comunidad.',
    vision = 'Ser una iglesia que transforma vidas, familias y comunidades a través del poder del Espíritu Santo.',
    address = 'Calle 45 #23-67, Barrio El Poblado',
    city = 'Medellín',
    country = 'Colombia',
    phone = '+57 4 123 4567',
    email = 'contacto@comunidadfe.org',
    website = 'www.comunidadfe.org',
    social_facebook = 'https://facebook.com/comunidadfe',
    social_instagram = 'https://instagram.com/comunidadfe',
    social_youtube = 'https://youtube.com/@comunidadfe',
    donation_info = 'Tu generosidad permite que continuemos transformando vidas.',
    bank_info = '{"banco": "Bancolombia", "numero": "123-456789-00", "titular": "Iglesia Comunidad de Fe", "tipo_cuenta": "Ahorros"}',
    service_schedule = '[{"day": "Domingo", "name": "Escuela Dominical", "time": "09:00"}, {"day": "Domingo", "name": "Culto Principal", "time": "10:30"}, {"day": "Miércoles", "name": "Estudio Bíblico", "time": "19:00"}, {"day": "Viernes", "name": "Reunión de Jóvenes", "time": "19:30"}]'
WHERE id = 1;

-- Usuarios (Contraseña admin123 y member123)
-- Hash bcrypt para "admin123": $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4e0TdMJ.jx.12b/W
-- Hash bcrypt para "member123": $2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi

INSERT INTO users (email, hashed_password, full_name, role, phone) VALUES
('admin@comunidadfe.org', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4e0TdMJ.jx.12b/W', 'Pastor Carlos Mendoza', 'admin', '+57 300 123 4567'),
('tesorero@comunidadfe.org', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4e0TdMJ.jx.12b/W', 'María González', 'admin', '+57 300 234 5678'),
('secretaria@comunidadfe.org', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4e0TdMJ.jx.12b/W', 'Ana Martínez', 'admin', '+57 300 345 6789'),
('juan.perez@email.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Juan Pérez', 'member', '+57 301 111 2222'),
('maria.rodriguez@email.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'María Rodríguez', 'member', '+57 301 222 3333'),
('pedro.sanchez@email.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Pedro Sánchez', 'member', '+57 301 333 4444'),
('lucia.gomez@email.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Lucía Gómez', 'member', '+57 301 444 5555'),
('carlos.lopez@email.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Carlos López', 'member', '+57 301 555 6666')
ON CONFLICT (email) DO NOTHING;

-- Eventos de ejemplo
INSERT INTO events (name, description, start_date, end_date, location, capacity, is_public, created_by_id) VALUES
('Culto Dominical', 'Servicio de adoración principal', CURRENT_DATE + INTERVAL '3 days', CURRENT_DATE + INTERVAL '3 days', 'Templo Principal', 500, true, 1),
('Estudio Bíblico', 'Estudio del libro de Romanos', CURRENT_DATE + INTERVAL '5 days', CURRENT_DATE + INTERVAL '5 days', 'Salón 2', 50, true, 1),
('Retiro de Jóvenes', 'Retiro espiritual para jóvenes', CURRENT_DATE + INTERVAL '14 days', CURRENT_DATE + INTERVAL '16 days', 'Finca El Refugio', 80, true, 1),
('Conferencia de Mujeres', 'Encuentro especial para mujeres', CURRENT_DATE + INTERVAL '21 days', CURRENT_DATE + INTERVAL '21 days', 'Templo Principal', 300, true, 1),
('Campaña Navideña', 'Celebración de Navidad', CURRENT_DATE + INTERVAL '30 days', CURRENT_DATE + INTERVAL '30 days', 'Templo Principal', 600, true, 1),
('Reunión de Líderes', 'Planificación mensual', CURRENT_DATE + INTERVAL '7 days', CURRENT_DATE + INTERVAL '7 days', 'Oficina Pastoral', 20, false, 1)
ON CONFLICT DO NOTHING;

-- Anuncios de ejemplo
INSERT INTO announcements (title, content, announcement_type, priority, is_public, is_active, created_by_id) VALUES
('Inscripciones Retiro de Jóvenes', 'Ya están abiertas las inscripciones para el retiro de jóvenes. Cupos limitados.', 'evento', 10, true, true, 1),
('Horario Especial Navidad', 'Durante diciembre tendremos horarios especiales de servicio.', 'general', 8, true, true, 1),
('Campaña de Alimentos', 'Estamos recolectando alimentos para familias necesitadas.', 'general', 7, true, true, 1),
('Nuevos Grupos de Estudio', 'Se abren nuevas células de estudio bíblico en diferentes zonas.', 'general', 5, true, true, 1),
('Reunión de Líderes', 'Recordatorio: reunión de líderes este sábado a las 9am.', 'interno', 3, false, true, 1)
ON CONFLICT DO NOTHING;

-- Donaciones de ejemplo
INSERT INTO donations (donor_name, donation_type, user_id, amount, payment_method, donation_date, note) VALUES
('Juan Pérez', 'diezmo', 4, 150000, 'transferencia', CURRENT_DATE - INTERVAL '5 days', 'Diezmo del mes'),
('María Rodríguez', 'ofrenda', 5, 50000, 'efectivo', CURRENT_DATE - INTERVAL '3 days', 'Ofrenda dominical'),
('Pedro Sánchez', 'diezmo', 6, 200000, 'transferencia', CURRENT_DATE - INTERVAL '7 days', 'Diezmo mensual'),
('Anónimo', 'misiones', NULL, 100000, 'efectivo', CURRENT_DATE - INTERVAL '1 day', 'Para misiones'),
('Lucía Gómez', 'especial', 7, 300000, 'transferencia', CURRENT_DATE - INTERVAL '2 days', 'Ofrenda especial navidad')
ON CONFLICT DO NOTHING;

-- Gastos de ejemplo
INSERT INTO expenses (description, amount, category_id, expense_date, status, vendor, created_by_id) VALUES
('Servicio de luz - Noviembre', 250000, 1, CURRENT_DATE - INTERVAL '10 days', 'paid', 'EPM', 1),
('Mantenimiento aire acondicionado', 180000, 2, CURRENT_DATE - INTERVAL '5 days', 'approved', 'TecniAire', 1),
('Materiales escuela dominical', 75000, 3, CURRENT_DATE - INTERVAL '3 days', 'pending', 'Librería Cristiana', 1),
('Decoración navideña', 120000, 4, CURRENT_DATE - INTERVAL '1 day', 'pending', 'Decoraciones Bogotá', 1)
ON CONFLICT DO NOTHING;

