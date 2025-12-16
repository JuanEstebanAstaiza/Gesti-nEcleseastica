-- =====================================================
-- DATOS INICIALES - EKKLESIA
-- Ejecutar después de crear las tablas
-- =====================================================

-- =====================================================
-- CONFIGURACIÓN DE LA IGLESIA
-- =====================================================
TRUNCATE TABLE church_config CASCADE;

INSERT INTO church_config (
    church_name, slogan, description, about_us, mission, vision,
    address, city, country, phone, email, website,
    primary_color, secondary_color,
    social_facebook, social_instagram, social_youtube,
    donation_info, bank_info, service_schedule
) VALUES (
    'Iglesia Comunidad de Fe',
    'Transformando vidas con el amor de Cristo',
    'Somos una comunidad de fe comprometida con el crecimiento espiritual y el servicio.',
    'La Iglesia Comunidad de Fe fue fundada en 1995 con la visión de crear un espacio donde las familias pudieran crecer juntas en fe y amor.',
    'Proclamar el evangelio de Jesucristo, formar discípulos comprometidos y servir a nuestra comunidad.',
    'Ser una iglesia que transforma vidas, familias y comunidades a través del poder del Espíritu Santo.',
    'Calle 45 #23-67, Barrio El Poblado',
    'Medellín',
    'Colombia',
    '+57 4 123 4567',
    'contacto@comunidadfe.org',
    'www.comunidadfe.org',
    '#8b5cf6',
    '#06b6d4',
    'https://facebook.com/comunidadfe',
    'https://instagram.com/comunidadfe',
    'https://youtube.com/@comunidadfe',
    'Tu generosidad permite que continuemos transformando vidas.',
    '{"banco": "Bancolombia", "numero": "123-456789-00", "titular": "Iglesia Comunidad de Fe", "tipo_cuenta": "Ahorros"}',
    '[{"day": "Domingo", "name": "Escuela Dominical", "time": "09:00"}, {"day": "Domingo", "name": "Culto Principal", "time": "10:30"}, {"day": "Miércoles", "name": "Estudio Bíblico", "time": "19:00"}, {"day": "Viernes", "name": "Reunión de Jóvenes", "time": "19:30"}]'
);

-- =====================================================
-- USUARIOS
-- Contraseñas: admin123, member123
-- Hash generado con bcrypt (passlib)
-- =====================================================

-- Limpiar usuarios existentes
TRUNCATE TABLE users CASCADE;

-- Administradores (contraseña: admin123)
INSERT INTO users (email, hashed_password, full_name, role, phone) VALUES
('admin@comunidadfe.org', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4e0TdMJ.jx.12b/W', 'Pastor Carlos Mendoza', 'admin', '+57 300 123 4567'),
('tesorero@comunidadfe.org', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4e0TdMJ.jx.12b/W', 'María González', 'admin', '+57 300 234 5678'),
('secretaria@comunidadfe.org', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4e0TdMJ.jx.12b/W', 'Ana Martínez', 'admin', '+57 300 345 6789');

-- Miembros (contraseña: member123)
INSERT INTO users (email, hashed_password, full_name, role, phone) VALUES
('juan.perez@email.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Juan Pérez', 'member', '+57 301 111 2222'),
('maria.rodriguez@email.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'María Rodríguez', 'member', '+57 301 222 3333'),
('pedro.sanchez@email.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Pedro Sánchez', 'member', '+57 301 333 4444'),
('lucia.gomez@email.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Lucía Gómez', 'member', '+57 301 444 5555'),
('carlos.lopez@email.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Carlos López', 'member', '+57 301 555 6666');

-- =====================================================
-- EVENTOS
-- =====================================================
INSERT INTO events (name, description, start_date, end_date, location, capacity, is_public, created_by_id) VALUES
('Culto Dominical', 'Servicio de adoración principal', CURRENT_DATE + INTERVAL '3 days', CURRENT_DATE + INTERVAL '3 days', 'Templo Principal', 500, true, 1),
('Estudio Bíblico', 'Estudio del libro de Romanos', CURRENT_DATE + INTERVAL '5 days', CURRENT_DATE + INTERVAL '5 days', 'Salón 2', 50, true, 1),
('Retiro de Jóvenes', 'Retiro espiritual para jóvenes', CURRENT_DATE + INTERVAL '14 days', CURRENT_DATE + INTERVAL '16 days', 'Finca El Refugio', 80, true, 1),
('Conferencia de Mujeres', 'Encuentro especial para mujeres', CURRENT_DATE + INTERVAL '21 days', CURRENT_DATE + INTERVAL '21 days', 'Templo Principal', 300, true, 1),
('Campaña Navideña', 'Celebración de Navidad', CURRENT_DATE + INTERVAL '30 days', CURRENT_DATE + INTERVAL '30 days', 'Templo Principal', 600, true, 1),
('Reunión de Líderes', 'Planificación mensual', CURRENT_DATE + INTERVAL '7 days', CURRENT_DATE + INTERVAL '7 days', 'Oficina Pastoral', 20, false, 1);

-- =====================================================
-- ANUNCIOS
-- =====================================================
INSERT INTO announcements (title, content, announcement_type, priority, is_public, is_active, created_by_id) VALUES
('Inscripciones Retiro de Jóvenes', 'Ya están abiertas las inscripciones para el retiro de jóvenes. Cupos limitados.', 'evento', 10, true, true, 1),
('Horario Especial Navidad', 'Durante diciembre tendremos horarios especiales de servicio.', 'general', 8, true, true, 1),
('Campaña de Alimentos', 'Estamos recolectando alimentos para familias necesitadas.', 'general', 7, true, true, 1),
('Nuevos Grupos de Estudio', 'Se abren nuevas células de estudio bíblico en diferentes zonas.', 'general', 5, true, true, 1),
('Reunión de Líderes', 'Recordatorio: reunión de líderes este sábado a las 9am.', 'interno', 3, false, true, 1);

-- =====================================================
-- DONACIONES DE EJEMPLO
-- =====================================================
INSERT INTO donations (donor_name, donation_type, user_id, amount, payment_method, donation_date, note) VALUES
('Juan Pérez', 'diezmo', 4, 150000, 'transferencia', CURRENT_DATE - INTERVAL '5 days', 'Diezmo del mes'),
('María Rodríguez', 'ofrenda', 5, 50000, 'efectivo', CURRENT_DATE - INTERVAL '3 days', 'Ofrenda dominical'),
('Pedro Sánchez', 'diezmo', 6, 200000, 'transferencia', CURRENT_DATE - INTERVAL '7 days', 'Diezmo mensual'),
('Anónimo', 'misiones', NULL, 100000, 'efectivo', CURRENT_DATE - INTERVAL '1 day', 'Para misiones'),
('Lucía Gómez', 'especial', 7, 300000, 'transferencia', CURRENT_DATE - INTERVAL '2 days', 'Ofrenda especial navidad');

-- =====================================================
-- GASTOS DE EJEMPLO
-- =====================================================
INSERT INTO expenses (description, amount, category_id, expense_date, status, vendor, created_by_id) VALUES
('Servicio de luz - Noviembre', 250000, 1, CURRENT_DATE - INTERVAL '10 days', 'paid', 'EPM', 1),
('Mantenimiento aire acondicionado', 180000, 2, CURRENT_DATE - INTERVAL '5 days', 'approved', 'TecniAire', 1),
('Materiales escuela dominical', 75000, 3, CURRENT_DATE - INTERVAL '3 days', 'pending', 'Librería Cristiana', 2),
('Decoración navideña', 120000, 4, CURRENT_DATE - INTERVAL '1 day', 'pending', 'Decoraciones Bogotá', 2);

