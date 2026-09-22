import sqlite3 as sq
from typing import List

conn = sq.connect("makerspace.db")
conn.row_factory = sq.Row
cur = conn.cursor()


def create_tables() -> None:
    """Create the tables in the database if they do not already exist."""
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            active BOOLEAN NOT NULL DEFAULT 1
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS equipment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            description TEXT,
            condition TEXT NOT NULL DEFAULT 'Good',
            available BOOLEAN NOT NULL DEFAULT 1
        )
        """
    )
    cur.execute(
        """
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
        )
        """
    )
    conn.commit()


# ---------------------------------------------------------------------------
# Members
# ---------------------------------------------------------------------------
def add_member(name: str, email: str, phone: str = "") -> int:
    """Add a new member to the database. Returns the new member's id."""
    cur.execute(
        "INSERT INTO members (name, email, phone) VALUES (?, ?, ?)",
        (name, email, phone),
    )
    conn.commit()
    assert cur.lastrowid is not None
    return cur.lastrowid


def list_members() -> List[sq.Row]:
    """Return a list of all members in the database."""
    cur.execute("SELECT * FROM members ORDER BY name")
    return cur.fetchall()


def get_member(member_id: int) -> sq.Row | None:
    """Retrieve a member's information by ID."""
    cur.execute("SELECT * FROM members WHERE id = ?", (member_id,))
    return cur.fetchone()


def update_member(member_id: int, name: str, email: str, phone: str) -> None:
    """Update member information."""
    cur.execute(
        "UPDATE members SET name = ?, email = ?, phone = ? WHERE id = ?",
        (name, email, phone, member_id),
    )
    conn.commit()


def delete_member(member_id: int) -> None:
    """Delete a member from the database."""
    cur.execute("DELETE FROM members WHERE id = ?", (member_id,))
    conn.commit()


def search_members_by_name(name: str) -> List[sq.Row]:
    """Search for members by name."""
    cur.execute("SELECT * FROM members WHERE name LIKE ?", (f"%{name}%",))
    return cur.fetchall()

def search_members_by_email(email: str) -> List[sq.Row]:
    """Search for members by email."""
    cur.execute("SELECT * FROM members WHERE email LIKE ?", (f"%{email}%",))
    return cur.fetchall()


# ---------------------------------------------------------------------------
# Equipment
# ---------------------------------------------------------------------------
def add_equipment(name: str, category: str = "General", description: str = "", condition: str = "Good") -> int:
    """Add new equipment to the database. Returns the new equipment's id."""
    cur.execute(
        "INSERT INTO equipment (name, category, description, condition) VALUES (?, ?, ?, ?)",
        (name, category, description, condition),
    )
    conn.commit()
    assert cur.lastrowid is not None
    return cur.lastrowid


def list_equipment() -> List[sq.Row]:
    """Return a list of all equipment in the database."""
    cur.execute("SELECT * FROM equipment ORDER BY name")
    return cur.fetchall()


def list_available_equipment() -> List[sq.Row]:
    """Return only equipment currently available for checkout."""
    cur.execute("SELECT * FROM equipment WHERE available = 1 ORDER BY name")
    return cur.fetchall()


def get_equipment(equipment_id: int) -> sq.Row | None:
    """Retrieve equipment information by ID."""
    cur.execute("SELECT * FROM equipment WHERE id = ?", (equipment_id,))
    return cur.fetchone()


def update_equipment(equipment_id: int, name: str, category: str, description: str, condition: str) -> None:
    """Update equipment information (name/category/description/condition;
    use set_equipment_availability() to change availability)."""
    cur.execute(
        "UPDATE equipment SET name = ?, category = ?, description = ?, condition = ? WHERE id = ?",
        (name, category, description, condition, equipment_id),
    )
    conn.commit()


def delete_equipment(equipment_id: int) -> None:
    """Delete equipment from the database."""
    cur.execute("DELETE FROM equipment WHERE id = ?", (equipment_id,))
    conn.commit()


def search_equipment_by_name(name: str) -> List[sq.Row]:
    """Search for equipment by name."""
    cur.execute("SELECT * FROM equipment WHERE name LIKE ?", (f"%{name}%",))
    return cur.fetchall()


def get_equipment_availability(equipment_id: int) -> bool:
    """Check if a specific piece of equipment is available."""
    cur.execute("SELECT available FROM equipment WHERE id = ?", (equipment_id,))
    result = cur.fetchone()
    return bool(result["available"]) if result else False


def set_equipment_availability(equipment_id: int, available: bool) -> None:
    """Set the availability status of a specific piece of equipment."""
    cur.execute(
        "UPDATE equipment SET available = ? WHERE id = ?",
        (1 if available else 0, equipment_id),
    )
    conn.commit()


# ---------------------------------------------------------------------------
# Loans
# ---------------------------------------------------------------------------
def create_loan(
    member_id: int, equipment_id: int, loan_date: str, due_date: str, token: str
) -> int:
    """Create a new loan record. Returns the new loan's id."""
    cur.execute(
        "INSERT INTO loans (token, member_id, equipment_id, loan_date, due_date) "
        "VALUES (?, ?, ?, ?, ?)",
        (token, member_id, equipment_id, loan_date, due_date),
    )
    conn.commit()
    assert cur.lastrowid is not None
    return cur.lastrowid


def close_loan(loan_id: int, return_date: str) -> None:
    """Close a loan record by setting the return date."""
    cur.execute(
        "UPDATE loans SET return_date = ? WHERE id = ?", (return_date, loan_id)
    )
    conn.commit()


def delete_loan(loan_id: int) -> None:
    """Delete a loan record outright (used by Undo, not by normal returns)."""
    cur.execute("DELETE FROM loans WHERE id = ?", (loan_id,))
    conn.commit()


def list_loans() -> List[sq.Row]:
    """Return a list of all loan records in the database."""
    cur.execute("SELECT * FROM loans ORDER BY loan_date DESC")
    return cur.fetchall()


def list_loans_with_names() -> List[sq.Row]:
    """Return every loan (open or closed), joined with member and equipment
    names — used by the CSV export report."""
    cur.execute(
        """
        SELECT loans.*, members.name AS member_name, equipment.name AS equipment_name
        FROM loans
        JOIN members ON loans.member_id = members.id
        JOIN equipment ON loans.equipment_id = equipment.id
        ORDER BY loans.loan_date DESC
        """
    )
    return cur.fetchall()

def get_loan_count_for_equipment(equipment_id: int) -> int:
    """Return the total number of loans for a specific piece of equipment."""
    cur.execute(
        "SELECT COUNT(*) AS loan_count FROM loans WHERE equipment_id = ?",
        (equipment_id,),
    )
    result = cur.fetchone()
    return result["loan_count"] if result else 0


def list_open_loans() -> List[sq.Row]:
    """Return active (not-yet-returned) loans, joined with member and
    equipment names for display."""
    cur.execute(
        """
        SELECT loans.*, members.name AS member_name, equipment.name AS equipment_name
        FROM loans
        JOIN members ON loans.member_id = members.id
        JOIN equipment ON loans.equipment_id = equipment.id
        WHERE loans.return_date IS NULL
        ORDER BY loans.due_date
        """
    )
    return cur.fetchall()


def get_loan_by_token(token: str) -> sq.Row | None:
    """Retrieve a loan record by its checkout token."""
    cur.execute("SELECT * FROM loans WHERE token = ?", (token,))
    return cur.fetchone()


def get_loans_by_member(member_id: int) -> List[sq.Row]:
    """Retrieve all loan records for a specific member."""
    cur.execute("SELECT * FROM loans WHERE member_id = ?", (member_id,))
    return cur.fetchall()


def get_loans_by_equipment(equipment_id: int) -> List[sq.Row]:
    """Retrieve all loan records for a specific piece of equipment."""
    cur.execute("SELECT * FROM loans WHERE equipment_id = ?", (equipment_id,))
    return cur.fetchall()


def get_active_loans() -> List[sq.Row]:
    """Retrieve all active (not returned) loan records."""
    cur.execute("SELECT * FROM loans WHERE return_date IS NULL")
    return cur.fetchall()


def get_overdue_loans(current_date: str) -> List[sq.Row]:
    """Retrieve all overdue loan records: still open and past their due date."""
    cur.execute(
        "SELECT * FROM loans WHERE return_date IS NULL AND due_date < ?",
        (current_date,),
    )
    return cur.fetchall()


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------
def get_top_borrowers(limit: int = 5) -> List[sq.Row]:
    """Members with the most loans overall, most-active first."""
    cur.execute(
        """
        SELECT members.name AS name, COUNT(*) AS loan_count
        FROM loans
        JOIN members ON loans.member_id = members.id
        GROUP BY members.id
        ORDER BY loan_count DESC
        LIMIT ?
        """,
        (limit,),
    )
    return cur.fetchall()


def get_popular_equipment(limit: int = 5) -> List[sq.Row]:
    """Equipment borrowed the most often, most-popular first."""
    cur.execute(
        """
        SELECT equipment.name AS name, COUNT(*) AS loan_count
        FROM loans
        JOIN equipment ON loans.equipment_id = equipment.id
        GROUP BY equipment.id
        ORDER BY loan_count DESC
        LIMIT ?
        """,
        (limit,),
    )
    return cur.fetchall()


def close_connection() -> None:
    """Close the database connection."""
    conn.close()