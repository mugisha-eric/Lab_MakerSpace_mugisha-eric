"""SQLite connection, schema setup, and data-access helpers.

Use schema.sql as the reference design. Keep SQL operations parameterised.
"""


import sqlite3 as sq

conn = sq.connect("makerspace.db")
cur = conn.cursor()

def create_tables() -> None:
    """Create the tables in the database if they do not already exist."""
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS equipment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            available BOOLEAN NOT NULL DEFAULT 1
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS loans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER NOT NULL,
            equipment_id INTEGER NOT NULL,
            loan_date TEXT NOT NULL,
            return_date TEXT,
            FOREIGN KEY (member_id) REFERENCES members(id),
            FOREIGN KEY (equipment_id) REFERENCES equipment(id)
        )
        """
    )
    conn.commit()

def add_member(name: str, email: str, phone: str) -> None:
    """Add a new member to the database."""
    cur.execute(
        "INSERT INTO members (name, email, phone) VALUES (?, ?, ?)",
        (name, email, phone)
    )
    conn.commit()

def list_members() -> list:
    """Return a list of all members in the database."""
    cur.execute("SELECT * FROM members")
    return cur.fetchall()

def add_equipment(name: str, description: str) -> None:
    """Add new equipment to the database."""
    cur.execute(
        "INSERT INTO equipment (name, description) VALUES (?, ?)",
        (name, description)
    )
    conn.commit()

def list_equipment() -> list:
    """Return a list of all equipment in the database."""
    cur.execute("SELECT * FROM equipment")
    return cur.fetchall()

def create_loan(member_id: int, equipment_id: int, loan_date: str) -> None:
    """Create a new loan record in the database."""
    cur.execute(
        "INSERT INTO loans (member_id, equipment_id, loan_date) VALUES (?, ?, ?)",
        (member_id, equipment_id, loan_date)
    )
    conn.commit()

def close_loan(loan_id: int, return_date: str) -> None:
    """Close a loan record by setting the return date."""
    cur.execute(
        "UPDATE loans SET return_date = ? WHERE id = ?",
        (return_date, loan_id)
    )
    conn.commit()

def list_loans() -> list:
    """Return a list of all loan records in the database."""
    cur.execute("SELECT * FROM loans")
    return cur.fetchall()

def search_members_by_name(name: str) -> list:
    """Search for members by name."""
    cur.execute(
        "SELECT * FROM members WHERE name LIKE ?",
        (f"%{name}%",)
    )
    return cur.fetchall()

def search_equipment_by_name(name: str) -> list:
    """Search for equipment by name."""
    cur.execute(
        "SELECT * FROM equipment WHERE name LIKE ?",
        (f"%{name}%",)
    )
    return cur.fetchall()

def update_member(member_id: int, name: str, email: str, phone: str) -> None:
    """Update member information."""
    cur.execute(
        "UPDATE members SET name = ?, email = ?, phone = ? WHERE id = ?",
        (name, email, phone, member_id)
    )
    conn.commit()

def update_equipment(equipment_id: int, name: str, description: str, available: bool) -> None:
    """Update equipment information."""
    cur.execute(
        "UPDATE equipment SET name = ?, description = ?, available = ? WHERE id = ?",
        (name, description, available, equipment_id)
    )
    conn.commit()

def delete_member(member_id: int) -> None:
    """Delete a member from the database."""
    cur.execute("DELETE FROM members WHERE id = ?", (member_id,))
    conn.commit()

def delete_equipment(equipment_id: int) -> None:
    """Delete equipment from the database."""
    cur.execute("DELETE FROM equipment WHERE id = ?", (equipment_id,))
    conn.commit()

def get_member(member_id: int) -> tuple:
    """Retrieve a member's information by ID."""
    cur.execute("SELECT * FROM members WHERE id = ?", (member_id,))
    return cur.fetchone()

def get_equipment(equipment_id: int) -> tuple:
    """Retrieve equipment information by ID."""
    cur.execute("SELECT * FROM equipment WHERE id = ?", (equipment_id,))
    return cur.fetchone()

# - provide report queries
def get_loans_by_member(member_id: int) -> list:
    """Retrieve all loan records for a specific member."""
    cur.execute(
        "SELECT * FROM loans WHERE member_id = ?",
        (member_id,)
    )
    return cur.fetchall()

def get_loans_by_equipment(equipment_id: int) -> list:
    """Retrieve all loan records for a specific piece of equipment."""
    cur.execute(
        "SELECT * FROM loans WHERE equipment_id = ?",
        (equipment_id,)
    )
    return cur.fetchall()

def get_active_loans() -> list:
    """Retrieve all active (not returned) loan records."""
    cur.execute(
        "SELECT * FROM loans WHERE return_date IS NULL"
    )
    return cur.fetchall()

def get_overdue_loans(current_date: str) -> list:
    """Retrieve all overdue loan records based on the current date."""
    cur.execute(
        "SELECT * FROM loans WHERE return_date IS NULL AND loan_date < ?",
        (current_date,)
    )
    return cur.fetchall()

def get_equipment_availability(equipment_id: int) -> bool:
    """Check if a specific piece of equipment is available."""
    cur.execute(
        "SELECT available FROM equipment WHERE id = ?",
        (equipment_id,)
    )
    result = cur.fetchone()
    return result[0] == 1 if result else False

def set_equipment_availability(equipment_id: int, available: bool) -> None:
    """Set the availability status of a specific piece of equipment."""
    cur.execute(
        "UPDATE equipment SET available = ? WHERE id = ?",
        (1 if available else 0, equipment_id)
    )
    conn.commit()

def close_connection() -> None:
    """Close the database connection."""
    conn.close()