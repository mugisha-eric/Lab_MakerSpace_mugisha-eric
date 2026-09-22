"""Create and seed the MakerSpace SQLite database once, then remove this file.

Run this from the folder that should contain makerspace.db:
    python /path/to/create_makerspace_db.py

Or specify the database explicitly:
    python create_makerspace_db.py --database /path/to/makerspace.db
"""

from __future__ import annotations

import argparse
import os
import sqlite3
import subprocess
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()

# This matches the tables used by the existing MakerSpace application.
SCHEMA = """
CREATE TABLE IF NOT EXISTS members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    active BOOLEAN NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS equipment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT,
    description TEXT,
    condition TEXT NOT NULL DEFAULT 'Good',
    available BOOLEAN NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS loans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token TEXT UNIQUE,
    member_id INTEGER NOT NULL,
    equipment_id INTEGER NOT NULL,
    loan_date TEXT NOT NULL,
    due_date TEXT,
    return_date TEXT,
    FOREIGN KEY (member_id) REFERENCES members(id),
    FOREIGN KEY (equipment_id) REFERENCES equipment(id)
);
"""

MEMBERS = (
    ("Alice Niyonizigiye", "alice.n@example.com", "+230 5251 1020", 1),
    ("Brian Mutesi", "brian.m@example.com", "+230 5251 1021", 1),
    ("Chantal Uwase", "chantal.u@example.com", None, 1),
    ("David Habimana", "david.h@example.com", "+230 5251 1023", 0),
)

EQUIPMENT = (
    ("Canon EOS R50", "Camera", "Mirrorless camera with 18–45mm lens", "Good", 0),
    ("Arduino Uno R3", "Electronics", "Microcontroller development board", "Good", 1),
    ("Prusa MINI+", "3D Printing", "Compact FDM 3D printer", "Good", 0),
    ("Bosch Drill Set", "Tools", "Cordless drill with drill-bit set", "Good", 1),
    ("Blue Yeti Microphone", "Audio", "USB condenser microphone", "Good", 0),
)

LOANS = (
    ("LOAN-2026-001", "alice.n@example.com", "Canon EOS R50", "2026-09-08", "2026-09-15", None),
    ("LOAN-2026-002", "brian.m@example.com", "Prusa MINI+", "2026-09-20", "2026-09-27", None),
    ("LOAN-2026-003", "chantal.u@example.com", "Blue Yeti Microphone", "2026-09-21", "2026-09-28", None),
    ("LOAN-2026-004", "alice.n@example.com", "Arduino Uno R3", "2026-09-05", "2026-09-12", "2026-09-11"),
    ("LOAN-2026-005", "brian.m@example.com", "Bosch Drill Set", "2026-08-28", "2026-09-04", "2026-09-04"),
)


def parse_arguments() -> Path:
    parser = argparse.ArgumentParser(description="Create and seed a MakerSpace SQLite database.")
    parser.add_argument(
        "--database",
        type=Path,
        default=Path.cwd() / "makerspace.db",
        help="Database to create or seed (default: ./makerspace.db)",
    )
    return parser.parse_args().database.expanduser().resolve()


def create_and_seed_database(database_path: Path) -> tuple[int, int, int]:
    """Create compatible tables and add only sample records that do not exist."""
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path)
    try:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript(SCHEMA)

        with connection:
            for name, email, phone, active in MEMBERS:
                connection.execute(
                    """
                    INSERT INTO members (name, email, phone, active)
                    SELECT ?, ?, ?, ?
                    WHERE NOT EXISTS (SELECT 1 FROM members WHERE email = ?)
                    """,
                    (name, email, phone, active, email),
                )

            for name, category, description, condition, available in EQUIPMENT:
                connection.execute(
                    """
                    INSERT INTO equipment (name, category, description, condition, available)
                    SELECT ?, ?, ?, ?, ?
                    WHERE NOT EXISTS (SELECT 1 FROM equipment WHERE name = ?)
                    """,
                    (name, category, description, condition, available, name),
                )

            for token, email, equipment_name, loan_date, due_date, return_date in LOANS:
                connection.execute(
                    """
                    INSERT INTO loans (
                        token, member_id, equipment_id, loan_date, due_date, return_date
                    )
                    SELECT ?, members.id, equipment.id, ?, ?, ?
                    FROM members
                    CROSS JOIN equipment
                    WHERE members.email = ?
                      AND equipment.name = ?
                      AND NOT EXISTS (SELECT 1 FROM loans WHERE token = ?)
                    """,
                    (token, loan_date, due_date, return_date, email, equipment_name, token),
                )

        return tuple(
            connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            for table in ("members", "equipment", "loans")
        )
    finally:
        connection.close()


def delete_this_setup_file() -> None:
    """Remove this file after success; Windows needs a short separate process."""
    if os.name != "nt":
        SCRIPT_PATH.unlink()
        return

    command = f'ping 127.0.0.1 -n 2 > nul & del /f /q "{SCRIPT_PATH}"'
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0) | getattr(
        subprocess, "DETACHED_PROCESS", 0
    )
    subprocess.Popen(
        ["cmd", "/c", command], creationflags=flags, close_fds=True
    )


def main() -> None:
    database_path = parse_arguments()
    members, equipment, loans = create_and_seed_database(database_path)
    print(f"Database ready: {database_path}")
    print(f"Verified: {members} members, {equipment} equipment items, {loans} loans.")
    delete_this_setup_file()


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"Setup failed; this file was kept: {error}", file=sys.stderr)
        raise
