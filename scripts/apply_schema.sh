#!/usr/bin/env bash
set -euo pipefail

DB_USER="${POSTGRES_USER:-ekklesia}"
DB_NAME="${POSTGRES_DB:-ekklesia}"
DB_HOST="${POSTGRES_HOST:-localhost}"
DB_PORT="${POSTGRES_PORT:-5432}"

PSQL="psql -h ${DB_HOST} -p ${DB_PORT} -U ${DB_USER} -d ${DB_NAME}"

if [[ -z "${1:-}" ]]; then
  SCHEMA_FILE="./app/db/sql/initial_schema.sql"
else
  SCHEMA_FILE="$1"
fi

echo "Aplicando esquema desde ${SCHEMA_FILE}..."
${PSQL} -f "${SCHEMA_FILE}"
echo "Esquema aplicado."

