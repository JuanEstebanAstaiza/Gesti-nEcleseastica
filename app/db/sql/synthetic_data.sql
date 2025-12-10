-- =====================================================
-- DATOS SINTÉTICOS PARA PRUEBAS - IGLESIA COMUNIDAD DE FE
-- =====================================================

-- =====================================================
-- CONFIGURACIÓN DE LA IGLESIA
-- =====================================================
UPDATE church_config SET
    church_name = 'Iglesia Comunidad de Fe',
    slogan = 'Transformando vidas con el amor de Cristo',
    description = 'Somos una comunidad de fe comprometida con el crecimiento espiritual, el servicio a la comunidad y la adoracion genuina a Dios.',
    about_us = 'La Iglesia Comunidad de Fe fue fundada en 1995 por el Pastor Carlos Mendoza con la vision de crear un espacio donde las familias pudieran crecer juntas en fe y amor. Hoy, despues de casi 30 anos, seguimos fieles a esa vision, alcanzando a nuestra ciudad con el mensaje de esperanza del Evangelio.',
    mission = 'Proclamar el evangelio de Jesucristo, formar discipulos comprometidos y servir a nuestra comunidad con amor y compasion.',
    vision = 'Ser una iglesia que transforma vidas, familias y comunidades a traves del poder del Espiritu Santo.',
    history = 'Nuestra iglesia comenzo como un pequeno grupo de oracion en el hogar de la familia Mendoza. A lo largo de los anos, Dios ha sido fiel en multiplicar nuestro ministerio, permitiendonos construir nuestro templo actual en 2005 y expandir nuestros programas de servicio comunitario.',
    address = 'Calle 45 #23-67, Barrio El Poblado',
    city = 'Medellin',
    country = 'Colombia',
    phone = '+57 4 123 4567',
    email = 'contacto@comunidadfe.org',
    website = 'www.comunidadfe.org',
    primary_color = '#8b5cf6',
    secondary_color = '#06b6d4',
    social_facebook = 'https://facebook.com/comunidadfe',
    social_instagram = 'https://instagram.com/comunidadfe',
    social_youtube = 'https://youtube.com/@comunidadfe',
    donation_info = 'Tu generosidad permite que continuemos transformando vidas. Cada donacion es utilizada de manera responsable para el crecimiento del Reino de Dios.',
    bank_info = '{"banco": "Bancolombia", "tipo_cuenta": "Ahorros", "numero": "123-456789-00", "titular": "Iglesia Comunidad de Fe NIT 800.123.456-7"}',
    service_schedule = '[{"day": "Domingo", "time": "09:00", "name": "Escuela Dominical"}, {"day": "Domingo", "time": "10:30", "name": "Culto Principal"}, {"day": "Miercoles", "time": "19:00", "name": "Estudio Biblico"}, {"day": "Viernes", "time": "19:30", "name": "Reunion de Jovenes"}]'
WHERE id = 1;

-- =====================================================
-- USUARIOS
-- =====================================================
-- Contraseña para todos: Test123! (hash bcrypt)
INSERT INTO users (email, hashed_password, full_name, role, phone, address, birth_date, is_active) VALUES
('admin@comunidadfe.org', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4FmcUMFFKVQgF5Ce', 'Pastor Carlos Mendoza', 'admin', '+57 300 111 2222', 'Calle 50 #30-45, Medellin', '1965-03-15', true),
('tesorero@comunidadfe.org', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4FmcUMFFKVQgF5Ce', 'Maria Garcia Lopez', 'admin', '+57 300 222 3333', 'Carrera 70 #25-30, Medellin', '1978-07-22', true),
('secretaria@comunidadfe.org', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4FmcUMFFKVQgF5Ce', 'Ana Martinez Ruiz', 'admin', '+57 300 333 4444', 'Calle 33 #65-20, Medellin', '1985-11-08', true),
('juan.perez@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4FmcUMFFKVQgF5Ce', 'Juan Carlos Perez', 'member', '+57 301 111 1111', 'Carrera 43 #10-25', '1980-05-20', true),
('maria.rodriguez@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4FmcUMFFKVQgF5Ce', 'Maria Elena Rodriguez', 'member', '+57 301 222 2222', 'Calle 80 #45-60', '1990-08-12', true),
('pedro.sanchez@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4FmcUMFFKVQgF5Ce', 'Pedro Antonio Sanchez', 'member', '+57 301 333 3333', 'Carrera 65 #32-15', '1975-12-03', true),
('lucia.gomez@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4FmcUMFFKVQgF5Ce', 'Lucia Fernanda Gomez', 'member', '+57 301 444 4444', 'Calle 55 #23-40', '1988-02-28', true),
('carlos.lopez@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4FmcUMFFKVQgF5Ce', 'Carlos Alberto Lopez', 'member', '+57 301 555 5555', 'Carrera 80 #12-35', '1995-06-15', true),
('andrea.martinez@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4FmcUMFFKVQgF5Ce', 'Andrea Patricia Martinez', 'member', '+57 301 666 6666', 'Calle 70 #55-20', '1992-09-10', true),
('roberto.diaz@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4FmcUMFFKVQgF5Ce', 'Roberto Jose Diaz', 'member', '+57 301 777 7777', 'Carrera 50 #40-15', '1970-04-25', true),
('sofia.torres@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4FmcUMFFKVQgF5Ce', 'Sofia Isabella Torres', 'member', '+57 301 888 8888', 'Calle 45 #30-50', '1998-01-18', true),
('daniel.herrera@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4FmcUMFFKVQgF5Ce', 'Daniel Alejandro Herrera', 'member', '+57 301 999 9999', 'Carrera 35 #60-25', '1983-11-30', true),
('visitante@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4FmcUMFFKVQgF5Ce', 'Visitante Demo', 'public', '+57 302 000 0000', '', '2000-01-01', true)
ON CONFLICT (email) DO UPDATE SET full_name = EXCLUDED.full_name;

-- =====================================================
-- EVENTOS
-- =====================================================
INSERT INTO events (name, description, start_date, end_date, start_time, end_time, location, capacity, is_public, is_featured, created_by_id) VALUES
('Culto de Navidad 2024', 'Celebremos juntos el nacimiento de nuestro Salvador con un culto especial lleno de adoracion, testimonios y un mensaje de esperanza.', '2024-12-24', '2024-12-24', '20:00', '22:00', 'Templo Principal', 500, true, true, 1),
('Retiro de Jovenes "Renuevate"', 'Un fin de semana para reconectar con Dios. Incluye hospedaje, alimentacion y transporte.', '2025-01-17', '2025-01-19', '08:00', '18:00', 'Finca El Refugio, Rionegro', 80, true, true, 1),
('Conferencia de Mujeres', 'Una jornada de empoderamiento espiritual para las mujeres de nuestra iglesia y comunidad.', '2025-02-15', '2025-02-15', '09:00', '17:00', 'Salon Multiple', 150, true, true, 1),
('Estudio Biblico: Libro de Romanos', 'Serie de 8 semanas estudiando la carta del apostol Pablo a los Romanos.', '2025-01-08', '2025-02-26', '19:00', '20:30', 'Salon 2', 40, true, false, 1),
('Campana de Alimentacion', 'Recoleccion de alimentos no perecederos para familias necesitadas de nuestra comunidad.', '2025-01-01', '2025-01-31', '00:00', '23:59', 'Recepcion del Templo', NULL, true, true, 1),
('Culto de Ano Nuevo', 'Iniciemos el 2025 en la presencia de Dios. Culto especial de accion de gracias y consagracion.', '2024-12-31', '2025-01-01', '22:00', '01:00', 'Templo Principal', 500, true, true, 1),
('Escuela para Padres', 'Taller mensual sobre crianza con principios biblicos.', '2025-01-25', '2025-01-25', '10:00', '12:00', 'Salon Multiple', 60, true, false, 1),
('Concierto de Alabanza', 'Noche de adoracion con musica en vivo. Entrada libre.', '2025-02-08', '2025-02-08', '19:00', '21:30', 'Templo Principal', 400, true, true, 1),
('Bautismo en Agua', 'Ceremonia de bautismo. Si deseas bautizarte, contacta a tu lider de celula.', '2025-02-02', '2025-02-02', '10:30', '12:00', 'Templo Principal', NULL, true, false, 1),
('Reunion de Lideres', 'Reunion mensual del equipo de liderazgo.', '2025-01-11', '2025-01-11', '08:00', '12:00', 'Oficinas Administrativas', 30, false, false, 1)
ON CONFLICT DO NOTHING;

-- =====================================================
-- MINISTERIOS
-- =====================================================
INSERT INTO ministries (name, description, leader_id, is_active, meeting_schedule) VALUES
('Ministerio de Alabanza', 'Equipo de musica y adoracion que lidera los tiempos de alabanza en cada culto.', 1, true, '{"dia": "Sabado", "hora": "16:00", "lugar": "Templo Principal"}'),
('Ministerio de Jovenes', 'Grupo de jovenes de 15 a 25 anos. Reuniones los viernes, actividades especiales y retiros.', 1, true, '{"dia": "Viernes", "hora": "19:30", "lugar": "Salon de Jovenes"}'),
('Ministerio de Ninos', 'Ensenanza biblica para ninos de 3 a 12 anos durante el culto dominical.', 2, true, '{"dia": "Domingo", "hora": "10:30", "lugar": "Salon Infantil"}'),
('Ministerio de Damas', 'Comunidad de mujeres que se reunen para oracion, estudio biblico y servicio.', 2, true, '{"dia": "Martes", "hora": "09:00", "lugar": "Salon 1"}'),
('Ministerio de Varones', 'Grupo de hombres comprometidos con el crecimiento espiritual y el liderazgo familiar.', 1, true, '{"dia": "Sabado", "hora": "07:00", "lugar": "Salon 2"}'),
('Ministerio de Intercesion', 'Equipo dedicado a la oracion por la iglesia, la ciudad y las naciones.', 3, true, '{"dia": "Miercoles", "hora": "06:00", "lugar": "Capilla"}'),
('Ministerio Social', 'Servicio a la comunidad: comedores, ropa, asistencia a familias vulnerables.', 3, true, '{"dia": "Sabado", "hora": "09:00", "lugar": "Centro Comunitario"}'),
('Ministerio de Matrimonios', 'Fortalecimiento de parejas a traves de estudios biblicos y actividades especiales.', 1, true, '{"dia": "Ultimo sabado del mes", "hora": "17:00", "lugar": "Salon Multiple"}')
ON CONFLICT DO NOTHING;

-- =====================================================
-- MIEMBROS DE MINISTERIOS
-- =====================================================
INSERT INTO ministry_members (ministry_id, user_id, role) VALUES
(1, 4, 'member'), (1, 5, 'member'), (1, 8, 'leader'),
(2, 8, 'leader'), (2, 9, 'member'), (2, 11, 'member'),
(3, 5, 'leader'), (3, 7, 'member'),
(4, 5, 'leader'), (4, 7, 'member'), (4, 9, 'member'),
(5, 4, 'leader'), (5, 6, 'member'), (5, 10, 'member'),
(6, 6, 'member'), (6, 7, 'member'),
(7, 6, 'leader'), (7, 9, 'member'), (7, 10, 'member'),
(8, 4, 'member'), (8, 5, 'member'), (8, 6, 'member'), (8, 7, 'member')
ON CONFLICT DO NOTHING;

-- =====================================================
-- DONACIONES (Ultimos 3 meses)
-- =====================================================
INSERT INTO donations (user_id, donor_name, donor_document, amount_tithe, amount_offering, amount_missions, amount_special, amount_total, is_cash, is_transfer, donation_date, week_number, envelope_number, created_by_id) VALUES
-- Diciembre 2024 - Semana 49
(4, 'Juan Carlos Perez', '1234567890', 150000, 50000, 20000, 0, 220000, true, false, '2024-12-01', 49, 'S49-001', 2),
(5, 'Maria Elena Rodriguez', '2345678901', 200000, 30000, 0, 50000, 280000, false, true, '2024-12-01', 49, 'S49-002', 2),
(6, 'Pedro Antonio Sanchez', '3456789012', 180000, 70000, 30000, 0, 280000, true, false, '2024-12-01', 49, 'S49-003', 2),
(7, 'Lucia Fernanda Gomez', '4567890123', 100000, 40000, 10000, 0, 150000, true, false, '2024-12-01', 49, 'S49-004', 2),
-- Diciembre 2024 - Semana 50
(4, 'Juan Carlos Perez', '1234567890', 150000, 50000, 0, 0, 200000, true, false, '2024-12-08', 50, 'S50-001', 2),
(8, 'Carlos Alberto Lopez', '5678901234', 80000, 20000, 10000, 0, 110000, false, true, '2024-12-08', 50, 'S50-002', 2),
(9, 'Andrea Patricia Martinez', '6789012345', 120000, 30000, 0, 0, 150000, true, false, '2024-12-08', 50, 'S50-003', 2),
(10, 'Roberto Jose Diaz', '7890123456', 250000, 100000, 50000, 0, 400000, false, true, '2024-12-08', 50, 'S50-004', 2),
-- Diciembre 2024 - Semana 51
(4, 'Juan Carlos Perez', '1234567890', 150000, 50000, 20000, 100000, 320000, true, false, '2024-12-15', 51, 'S51-001', 2),
(5, 'Maria Elena Rodriguez', '2345678901', 200000, 30000, 0, 200000, 430000, false, true, '2024-12-15', 51, 'S51-002', 2),
(6, 'Pedro Antonio Sanchez', '3456789012', 180000, 70000, 30000, 50000, 330000, true, false, '2024-12-15', 51, 'S51-003', 2),
(11, 'Sofia Isabella Torres', '8901234567', 50000, 20000, 0, 0, 70000, true, false, '2024-12-15', 51, 'S51-004', 2),
(12, 'Daniel Alejandro Herrera', '9012345678', 300000, 50000, 30000, 100000, 480000, false, true, '2024-12-15', 51, 'S51-005', 2),
-- Diciembre 2024 - Semana 52 (Navidad)
(4, 'Juan Carlos Perez', '1234567890', 150000, 100000, 50000, 500000, 800000, true, false, '2024-12-22', 52, 'S52-001', 2),
(5, 'Maria Elena Rodriguez', '2345678901', 200000, 80000, 30000, 300000, 610000, false, true, '2024-12-22', 52, 'S52-002', 2),
(6, 'Pedro Antonio Sanchez', '3456789012', 180000, 120000, 50000, 200000, 550000, true, false, '2024-12-22', 52, 'S52-003', 2),
(7, 'Lucia Fernanda Gomez', '4567890123', 100000, 50000, 20000, 100000, 270000, true, false, '2024-12-22', 52, 'S52-004', 2),
(8, 'Carlos Alberto Lopez', '5678901234', 80000, 40000, 10000, 50000, 180000, false, true, '2024-12-22', 52, 'S52-005', 2),
(9, 'Andrea Patricia Martinez', '6789012345', 120000, 60000, 0, 150000, 330000, true, false, '2024-12-22', 52, 'S52-006', 2),
(10, 'Roberto Jose Diaz', '7890123456', 250000, 150000, 80000, 400000, 880000, false, true, '2024-12-22', 52, 'S52-007', 2),
-- Donaciones anonimas
(NULL, 'Anonimo', NULL, 0, 500000, 0, 0, 500000, true, false, '2024-12-22', 52, 'S52-008', 2),
(NULL, 'Hermano en Cristo', NULL, 100000, 100000, 100000, 0, 300000, true, false, '2024-12-15', 51, 'S51-006', 2)
ON CONFLICT DO NOTHING;

-- =====================================================
-- TRANSMISIONES EN VIVO
-- =====================================================
INSERT INTO live_streams (title, description, youtube_video_id, platform, is_live, is_featured, scheduled_at, view_count, created_by_id) VALUES
('Culto Dominical - 15 Diciembre 2024', 'Mensaje: "El verdadero significado de la Navidad" - Pastor Carlos Mendoza', 'dQw4w9WgXcQ', 'youtube', false, false, '2024-12-15 10:30:00', 245, 1),
('Estudio Biblico - Romanos Capitulo 8', 'Continuamos nuestra serie sobre la carta a los Romanos', 'dQw4w9WgXcQ', 'youtube', false, false, '2024-12-11 19:00:00', 89, 1),
('Culto de Navidad 2024', 'Culto especial de Nochebuena. Mensaje de esperanza y celebracion.', 'dQw4w9WgXcQ', 'youtube', false, true, '2024-12-24 20:00:00', 512, 1),
('Culto Dominical - 22 Diciembre 2024', 'Mensaje: "Preparando el corazon para el nuevo ano" - Pastor Carlos Mendoza', 'dQw4w9WgXcQ', 'youtube', false, false, '2024-12-22 10:30:00', 198, 1),
('Culto de Ano Nuevo 2025', 'Recibamos el nuevo ano en la presencia de Dios', 'dQw4w9WgXcQ', 'youtube', false, true, '2024-12-31 22:00:00', 0, 1)
ON CONFLICT DO NOTHING;

-- =====================================================
-- CONTENIDO PÚBLICO
-- =====================================================
INSERT INTO public_content (slug, title, content, excerpt, content_type, is_published, is_featured, published_at, created_by_id) VALUES
('quienes-somos', 'Quienes Somos', 
'## Nuestra Historia

La Iglesia Comunidad de Fe nacio en 1995 como un pequeno grupo de oracion en el hogar de la familia Mendoza. Lo que comenzo con apenas 12 personas reunidas cada miercoles, hoy se ha convertido en una comunidad vibrante de mas de 500 miembros activos.

## Nuestro Pastor

El Pastor Carlos Mendoza ha liderado nuestra congregacion desde su fundacion. Con mas de 30 anos de ministerio, su pasion por la Palabra de Dios y el cuidado pastoral han sido fundamentales en el crecimiento de nuestra iglesia.

## Lo Que Creemos

- Creemos en un solo Dios, eternamente existente en tres personas: Padre, Hijo y Espiritu Santo.
- Creemos en la inspiracion divina de las Sagradas Escrituras.
- Creemos en la salvacion por gracia mediante la fe en Jesucristo.
- Creemos en la segunda venida de Cristo.

## Nuestra Comunidad

Somos una familia diversa: jovenes, adultos, ancianos, solteros, casados, profesionales y estudiantes. Nos une el amor a Dios y el compromiso de servir a nuestra ciudad.', 
'Conoce nuestra historia, valores y lo que creemos como iglesia.', 'page', true, true, NOW(), 1),

('como-donar', 'Como Donar', 
'## Tu Generosidad Hace la Diferencia

Gracias por considerar apoyar la obra de Dios a traves de nuestra iglesia. Cada donacion es administrada con integridad y transparencia.

## Formas de Donar

### 1. En el Culto
Puedes dar tu ofrenda durante nuestros servicios dominicales. Tenemos sobres disponibles en la entrada.

### 2. Transferencia Bancaria
- **Banco:** Bancolombia
- **Tipo de cuenta:** Ahorros
- **Numero:** 123-456789-00
- **Titular:** Iglesia Comunidad de Fe
- **NIT:** 800.123.456-7

### 3. En Linea
Proximamente habilitaremos pagos en linea a traves de nuestra plataforma.

## Tipos de Donacion

- **Diezmo:** El 10% de tus ingresos, como acto de obediencia y gratitud a Dios.
- **Ofrenda:** Donacion voluntaria para el sostenimiento de la iglesia.
- **Misiones:** Apoyo a proyectos misioneros nacionales e internacionales.
- **Donaciones Especiales:** Para proyectos especificos como construccion, equipos, etc.

## Transparencia

Publicamos informes financieros trimestrales disponibles para todos nuestros miembros.', 
'Conoce las diferentes formas en que puedes apoyar nuestra iglesia.', 'page', true, true, NOW(), 1),

('horarios', 'Horarios de Servicios', 
'## Servicios Semanales

### Domingo
- **09:00 AM** - Escuela Dominical (todas las edades)
- **10:30 AM** - Culto Principal de Adoracion

### Miercoles
- **07:00 PM** - Estudio Biblico

### Viernes
- **07:30 PM** - Reunion de Jovenes (15-25 anos)

## Ubicacion

Calle 45 #23-67, Barrio El Poblado, Medellin

## Estacionamiento

Contamos con parqueadero gratuito para 50 vehiculos.

## Servicio para Ninos

Durante el culto dominical ofrecemos programas especiales para ninos de 3 a 12 anos.', 
'Conoce nuestros horarios de servicios y actividades semanales.', 'page', true, false, NOW(), 1)
ON CONFLICT (slug) DO UPDATE SET content = EXCLUDED.content;

-- =====================================================
-- ANUNCIOS
-- =====================================================
INSERT INTO announcements (title, content, announcement_type, priority, is_public, is_active, start_date, end_date, created_by_id) VALUES
('Inscripciones Retiro de Jovenes', 'Ya estan abiertas las inscripciones para el Retiro de Jovenes "Renuevate" del 17 al 19 de enero. Cupos limitados. Costo: $150,000 incluye transporte, hospedaje y alimentacion.', 'evento', 1, true, true, '2024-12-15', '2025-01-15', 1),
('Horario Especial Navidad', 'Este 24 de diciembre nuestro culto sera a las 8:00 PM. No habra servicio el 25 de diciembre. Los esperamos!', 'general', 2, true, true, '2024-12-20', '2024-12-25', 1),
('Campana de Alimentos', 'Durante todo enero estaremos recibiendo alimentos no perecederos para familias necesitadas. Puedes traerlos a la recepcion del templo.', 'social', 1, true, true, '2024-12-28', '2025-01-31', 1),
('Nuevas Celulas de Estudio', 'Estamos abriendo nuevos grupos de celulas en diferentes sectores de la ciudad. Si te interesa liderar o participar, habla con tu pastor de zona.', 'general', 0, true, true, '2024-12-01', '2025-02-28', 1),
('Actualizacion de Datos', 'Estamos actualizando nuestra base de datos. Por favor, si has cambiado de direccion, telefono o correo, notificalo en secretaria.', 'administrativo', 0, false, true, '2024-12-01', '2025-01-31', 3)
ON CONFLICT DO NOTHING;

-- =====================================================
-- PETICIONES DE ORACIÓN
-- =====================================================
INSERT INTO prayer_requests (user_id, requester_name, request_text, is_public, is_answered, prayer_count) VALUES
(4, 'Juan Carlos', 'Pido oracion por la salud de mi madre que esta en el hospital.', true, false, 15),
(5, 'Maria Elena', 'Oremos por mi hijo que esta buscando trabajo.', true, false, 8),
(6, 'Pedro', 'Necesito oracion por mi matrimonio. Estamos pasando por momentos dificiles.', false, false, 0),
(7, 'Lucia', 'Gracias a Dios! Mi hermano fue sanado. Gloria a Dios!', true, true, 23),
(NULL, 'Anonimo', 'Oracion por la paz de mi familia.', true, false, 12),
(8, 'Carlos', 'Pido oracion por mi viaje misionero a la costa.', true, false, 19),
(9, 'Andrea', 'Oremos por los ninos del ministerio infantil.', true, false, 7)
ON CONFLICT DO NOTHING;

-- =====================================================
-- GASTOS (Ultimos 2 meses)
-- =====================================================
INSERT INTO expenses (category_id, subcategory_id, description, amount, expense_date, vendor_name, payment_method, status, created_by_id, approved_by_id, approved_at) VALUES
-- Servicios Publicos
(1, 1, 'Pago energia electrica diciembre', 850000, '2024-12-05', 'EPM', 'transferencia', 'paid', 3, 1, '2024-12-05'),
(1, 2, 'Pago agua diciembre', 180000, '2024-12-05', 'EPM', 'transferencia', 'paid', 3, 1, '2024-12-05'),
(1, 4, 'Servicio de internet diciembre', 150000, '2024-12-01', 'Claro', 'transferencia', 'paid', 3, 1, '2024-12-01'),
-- Arriendo
(2, NULL, 'Arriendo local diciembre', 3500000, '2024-12-01', 'Inmobiliaria XYZ', 'transferencia', 'paid', 3, 1, '2024-12-01'),
-- Salarios
(3, 6, 'Honorarios pastor diciembre', 4000000, '2024-12-15', 'Pastor Carlos Mendoza', 'transferencia', 'paid', 3, 1, '2024-12-15'),
(3, 7, 'Salario secretaria diciembre', 1800000, '2024-12-15', 'Ana Martinez', 'transferencia', 'paid', 3, 1, '2024-12-15'),
(3, 8, 'Pago personal limpieza diciembre', 600000, '2024-12-15', 'Rosa Jimenez', 'efectivo', 'paid', 3, 1, '2024-12-15'),
-- Mantenimiento
(4, 9, 'Reparacion tuberia bano', 250000, '2024-12-10', 'Plomero Jose', 'efectivo', 'paid', 3, 1, '2024-12-10'),
(4, 10, 'Reparacion luces salon principal', 180000, '2024-12-12', 'Electricista Pedro', 'efectivo', 'paid', 3, 1, '2024-12-12'),
-- Suministros
(5, NULL, 'Compra articulos de oficina', 320000, '2024-12-08', 'Papeleria Central', 'efectivo', 'paid', 3, 1, '2024-12-08'),
(5, NULL, 'Productos de limpieza', 180000, '2024-12-08', 'Exito', 'efectivo', 'paid', 3, 1, '2024-12-08'),
-- Eventos
(6, NULL, 'Decoracion culto de Navidad', 450000, '2024-12-20', 'Decoraciones Maria', 'efectivo', 'paid', 3, 1, '2024-12-20'),
(6, NULL, 'Refrigerios culto de Navidad', 350000, '2024-12-24', 'Panaderia El Trigal', 'efectivo', 'paid', 3, 1, '2024-12-24'),
-- Misiones
(8, NULL, 'Apoyo misionero Costa Atlantica', 500000, '2024-12-15', 'Mision Costa', 'transferencia', 'paid', 3, 1, '2024-12-15'),
-- Pendientes
(1, 1, 'Pago energia electrica enero (estimado)', 900000, '2025-01-05', 'EPM', 'transferencia', 'pending', 3, NULL, NULL),
(2, NULL, 'Arriendo local enero', 3500000, '2025-01-01', 'Inmobiliaria XYZ', 'transferencia', 'approved', 3, 1, NOW())
ON CONFLICT DO NOTHING;

-- =====================================================
-- REGISTRACIONES A EVENTOS
-- =====================================================
INSERT INTO registrations (event_id, user_id, attendee_name, attendee_email, attendee_phone, registered_at) VALUES
-- Retiro de Jovenes
(2, 8, 'Carlos Alberto Lopez', 'carlos.lopez@email.com', '+57 301 555 5555', NOW()),
(2, 9, 'Andrea Patricia Martinez', 'andrea.martinez@email.com', '+57 301 666 6666', NOW()),
(2, 11, 'Sofia Isabella Torres', 'sofia.torres@email.com', '+57 301 888 8888', NOW()),
(2, NULL, 'Miguel Angel Vargas', 'miguel.vargas@email.com', '+57 302 111 2222', NOW()),
(2, NULL, 'Camila Restrepo', 'camila.restrepo@email.com', '+57 302 333 4444', NOW()),
-- Conferencia de Mujeres
(3, 5, 'Maria Elena Rodriguez', 'maria.rodriguez@email.com', '+57 301 222 2222', NOW()),
(3, 7, 'Lucia Fernanda Gomez', 'lucia.gomez@email.com', '+57 301 444 4444', NOW()),
(3, 9, 'Andrea Patricia Martinez', 'andrea.martinez@email.com', '+57 301 666 6666', NOW()),
(3, 11, 'Sofia Isabella Torres', 'sofia.torres@email.com', '+57 301 888 8888', NOW())
ON CONFLICT DO NOTHING;

-- =====================================================
-- FIN DE DATOS SINTÉTICOS
-- =====================================================
SELECT 'Datos sinteticos cargados exitosamente!' as resultado;

