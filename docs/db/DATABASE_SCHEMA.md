# Esquema de Datos

## ERD ASCII (Fase 1)
```
Users 1---n Donations
Users 1---n Documents
Users 1---n Events
Events 1---n Donations
Events 1---n Documents
Donations 1---n Documents
```

## Tablas
- `users`: credenciales, rol (`public/member/admin`), actividad.
- `events`: eventos eclesiásticos; referencia opcional a usuario creador.
- `donations`: tipo (`diezmo/ofrenda/misiones/especial`), monto, medio de pago, notas, fecha.
- `documents`: archivos vinculados a donaciones/usuarios/eventos; metadata (mime, tamaño, checksum, visibilidad).

## Índices
- `users.email`, `users.role`
- `events.created_by_id`
- `donations.user_id`, `donations.event_id`, `donations.donation_type`, `donations.donation_date`
- `documents.donation_id`, `documents.user_id`, `documents.event_id`

## Migraciones
- Sin Alembic. Usar scripts SQL manuales:
  - `app/db/sql/initial_schema.sql`
- Aplicación:
  ```bash
  docker exec -i ekklesia_db psql -U ${POSTGRES_USER:-ekklesia} -d ${POSTGRES_DB:-ekklesia} -f /code/app/db/sql/initial_schema.sql
  ```

