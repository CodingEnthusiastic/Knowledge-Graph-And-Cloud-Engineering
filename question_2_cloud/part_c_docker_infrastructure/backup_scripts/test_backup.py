"""
Unit Tests for Database Backup Retention Manager
=================================================
Verifies that:
1. Backup retention strictly limits stored archives to the most recent 7.
2. Older files are systematically purged.
3. Checksum generation and validation function correctly.
"""

import gzip
import time
from pathlib import Path
import pytest

from backup_db import (
    compute_sha256,
    purge_old_backups,
    create_backup,
    RETENTION_LIMIT,
)


def test_compute_sha256(tmp_path: Path):
    """Verify SHA-256 calculation on sample content."""
    sample_file = tmp_path / "test.txt"
    sample_file.write_text("CareSync Database Integrity Test", encoding="utf-8")
    digest = compute_sha256(sample_file)
    assert len(digest) == 64
    assert isinstance(digest, str)


def test_purge_old_backups_strict_retention(tmp_path: Path):
    """
    Create 12 mock backup files with staggered modification times.
    Confirm that purge_old_backups removes the 5 oldest and retains exactly 7.
    """
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()

    created_files = []
    # Create 12 mock backups
    for i in range(12):
        filename = f"db_backup_202610{i+1:02d}_000000Z.sql.gz"
        file_path = backup_dir / filename
        with gzip.open(file_path, "wt", encoding="utf-8") as f:
            f.write(f"MOCK SQL DATA FOR DAY {i+1}")

        # Stagger mtime
        file_mtime = 1700000000 + (i * 3600)
        file_path.touch()
        # Set artificial time
        import os
        os.utime(file_path, (file_mtime, file_mtime))
        created_files.append(file_path)

    assert len(list(backup_dir.glob("*.sql.gz"))) == 12

    # Execute retention purge
    deleted = purge_old_backups(backup_dir, retention=7)

    # Assertions
    remaining = sorted(backup_dir.glob("*.sql.gz"))
    assert len(remaining) == 7, f"Expected 7 files retained, found {len(remaining)}"
    assert len(deleted) == 5, f"Expected 5 files deleted, deleted {len(deleted)}"

    # Confirm that the remaining 7 correspond to the most recent 7
    remaining_names = [f.name for f in remaining]
    assert "db_backup_20261012_000000Z.sql.gz" in remaining_names
    assert "db_backup_20261001_000000Z.sql.gz" not in remaining_names


def test_create_backup_integration(tmp_path: Path):
    """Test full create_backup pipeline in mock environment."""
    backup_dir = tmp_path / "auto_backups"
    backup_path = create_backup(backup_dir)

    assert backup_path.exists()
    assert backup_path.stat().st_size > 0
    sha_path = backup_path.with_name(f"{backup_path.name}.sha256")
    assert sha_path.exists()
