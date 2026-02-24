"""
One-time migration script to remap all existing deals from old stage system to new stage system,
add new model columns, and clear stale insights.

Old -> New Mapping:
  1-Legal    -> 6-Lease Review (numeric 6)
  2-LOI      -> 5-LOI Negotiation (numeric 5)
  3-Touring  -> 3-Touring (numeric 3)
  4-Inquiry  -> 1-Inquiry (numeric 1)
  5-Complete -> 7-Complete (numeric 7)
  6-Idle     -> 8-On Hold (numeric 8)
  7-Dead     -> 9-Dead (numeric 9)

Usage:
  python scripts/migrate_stages.py             # Dry run
  python scripts/migrate_stages.py --execute   # Apply changes
"""
import sqlite3
import sys
import shutil
from datetime import datetime

MIGRATION_MAP = {
    "1-Legal":    ("6-Lease Review",    6),
    "2-LOI":      ("5-LOI Negotiation", 5),
    "3-Touring":  ("3-Touring",         3),
    "4-Inquiry":  ("1-Inquiry",         1),
    "5-Complete": ("7-Complete",        7),
    "6-Idle":     ("8-On Hold",         8),
    "7-Dead":     ("9-Dead",            9),
}


def migrate(db_path: str = "harborcap.db", dry_run: bool = True):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Show current state
    cursor.execute("SELECT COUNT(*) FROM deals")
    total = cursor.fetchone()[0]
    print(f"Total deals in database: {total}")

    cursor.execute("SELECT stage, COUNT(*) FROM deals GROUP BY stage ORDER BY stage")
    print("\nCurrent stage distribution:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]} deals")

    # 2. Add new columns if they don't exist
    for col, col_type in [
        ("probability_score", "INTEGER"),
        ("deal_priority", "VARCHAR(20)"),
        ("scope", "VARCHAR(20)"),
        ("severity", "VARCHAR(20)"),
        ("is_auto_generated", "BOOLEAN"),
        ("tags", "TEXT"),
    ]:
        try:
            # Check which table the column belongs to
            if col in ("scope", "severity", "is_auto_generated", "tags"):
                cursor.execute(f"ALTER TABLE ai_insights ADD COLUMN {col} {col_type}")
                print(f"Added {col} column to ai_insights")
            else:
                cursor.execute(f"ALTER TABLE deals ADD COLUMN {col} {col_type}")
                print(f"Added {col} column to deals")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                pass  # Column already exists
            else:
                print(f"Warning: {e}")

    # Set defaults for new ai_insights columns
    if not dry_run:
        cursor.execute("UPDATE ai_insights SET scope = 'property' WHERE scope IS NULL")
        cursor.execute("UPDATE ai_insights SET is_auto_generated = 0 WHERE is_auto_generated IS NULL")

    # 3. Perform stage migration
    print(f"\n{'=' * 50}")
    migrated = 0
    for old_stage, (new_stage, new_numeric) in MIGRATION_MAP.items():
        cursor.execute("SELECT COUNT(*) FROM deals WHERE stage = ?", (old_stage,))
        count = cursor.fetchone()[0]
        prefix = "[DRY RUN] " if dry_run else ""
        print(f"{prefix}Migrating {old_stage} -> {new_stage} ({count} deals)")

        if not dry_run and count > 0:
            cursor.execute(
                "UPDATE deals SET stage = ?, stage_numeric = ? WHERE stage = ?",
                (new_stage, new_numeric, old_stage)
            )
            migrated += cursor.rowcount

    # 4. Clear stale AI insights (they reference old stage names)
    cursor.execute("SELECT COUNT(*) FROM ai_insights")
    insight_count = cursor.fetchone()[0]
    if insight_count > 0:
        prefix = "[DRY RUN] " if dry_run else ""
        print(f"\n{prefix}Clearing {insight_count} stale AI insights (will be regenerated)")
        if not dry_run:
            cursor.execute("DELETE FROM ai_insights")

    # 5. Commit or report
    if not dry_run:
        conn.commit()
        print(f"\nMigration complete. {migrated} deals updated.")

        # Verify
        cursor.execute("SELECT stage, stage_numeric, COUNT(*) FROM deals GROUP BY stage, stage_numeric ORDER BY stage_numeric")
        print("\nNew stage distribution:")
        for row in cursor.fetchall():
            print(f"  {row[0]} (numeric={row[1]}): {row[2]} deals")
    else:
        print(f"\nDry run complete. No changes made. Run with --execute to apply.")

    conn.close()


if __name__ == "__main__":
    dry_run = "--execute" not in sys.argv
    db_path = "harborcap.db"

    # Find the database
    import os
    if not os.path.exists(db_path):
        alt = os.path.join(os.path.dirname(__file__), "..", "harborcap.db")
        if os.path.exists(alt):
            db_path = alt

    if not dry_run:
        # Backup first
        backup_path = f"{db_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(db_path, backup_path)
        print(f"Backup created: {backup_path}\n")

    migrate(db_path, dry_run)
