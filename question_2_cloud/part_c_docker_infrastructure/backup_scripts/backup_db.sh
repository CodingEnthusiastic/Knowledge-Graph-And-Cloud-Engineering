#!/usr/bin/env bash
# ==============================================================================
# CareSync AI Database Backup Script (Automated Daily Rotation)
# ==============================================================================
# - Executes pg_dump from PostgreSQL container or host
# - Compresses output using gzip with UTC timestamp
# - Generates SHA-256 checksum for tamper verification
# - Retains exactly the last 7 backups, purging older files
# ==============================================================================

set -euo pipefail

# Configuration
BACKUP_DIR="${BACKUP_DIR:-/var/backups/caresync_db}"
CONTAINER_NAME="${CONTAINER_NAME:-caresync_postgres}"
DB_NAME="${POSTGRES_DB:-app_db}"
DB_USER="${POSTGRES_USER:-app_user}"
RETENTION_DAYS=7
TIMESTAMP=$(date -u +"%Y%m%d_%H%M%SZ")
BACKUP_FILE="${BACKUP_DIR}/db_backup_${TIMESTAMP}.sql.gz"

echo "=== Starting CareSync DB Backup at $(date -u) ==="

# Create backup directory if it does not exist
mkdir -p "${BACKUP_DIR}"

# Execute pg_dump inside docker container with gzip stream
if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "[INFO] Running pg_dump inside Docker container '${CONTAINER_NAME}'..."
    docker exec "${CONTAINER_NAME}" pg_dump -U "${DB_USER}" -d "${DB_NAME}" --clean --if-exists | gzip > "${BACKUP_FILE}"
else
    echo "[INFO] Container not found; attempting local pg_dump..."
    pg_dump -U "${DB_USER}" -d "${DB_NAME}" --clean --if-exists | gzip > "${BACKUP_FILE}"
fi

# Verify backup file size
if [ ! -s "${BACKUP_FILE}" ]; then
    echo "[ERROR] Backup failed! Output file is empty."
    rm -f "${BACKUP_FILE}"
    exit 1
fi

# Generate SHA256 checksum
sha256sum "${BACKUP_FILE}" > "${BACKUP_FILE}.sha256"
FILE_SIZE=$(du -h "${BACKUP_FILE}" | cut -f1)
echo "[SUCCESS] Backup created: ${BACKUP_FILE} (Size: ${FILE_SIZE})"

# ==============================================================================
# Retention Policy: Keep only the 7 most recent backup archives
# ==============================================================================
echo "[INFO] Applying retention policy: Keeping latest ${RETENTION_DAYS} backups..."

# List backups sorted by timestamp descending, skip the first 7, delete the rest
find "${BACKUP_DIR}" -maxdepth 1 -name "db_backup_*.sql.gz" -type f | sort -r | tail -n +$((RETENTION_DAYS + 1)) | while read -r old_backup; do
    echo "[PURGE] Deleting outdated backup: ${old_backup}"
    rm -f "${old_backup}"
    rm -f "${old_backup}.sha256"
done

TOTAL_RETAINED=$(find "${BACKUP_DIR}" -maxdepth 1 -name "db_backup_*.sql.gz" -type f | wc -l)
echo "[INFO] Retention complete. Current active backups retained: ${TOTAL_RETAINED}"
echo "=== Backup Process Completed Successfully ==="
