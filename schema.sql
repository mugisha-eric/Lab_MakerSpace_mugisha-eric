-- Initial SQLite design for the Campus MakerSpace Checkout System.
-- Apply this schema once, or have database.py run equivalent statements on first launch.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS members (
    member_id INTEGER PRIMARY KEY,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS equipment (
    equipment_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    item_condition TEXT NOT NULL DEFAULT 'Good',
    is_available INTEGER NOT NULL DEFAULT 1 CHECK (is_available IN (0, 1)),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS loans (
    loan_id INTEGER PRIMARY KEY,
    member_id INTEGER NOT NULL,
    equipment_id INTEGER NOT NULL,
    checkout_date TEXT NOT NULL,
    due_date TEXT NOT NULL,
    returned_date TEXT,
    FOREIGN KEY (member_id) REFERENCES members(member_id),
    FOREIGN KEY (equipment_id) REFERENCES equipment(equipment_id)
);

CREATE INDEX IF NOT EXISTS idx_loans_member_id ON loans(member_id);
CREATE INDEX IF NOT EXISTS idx_loans_equipment_id ON loans(equipment_id);
CREATE INDEX IF NOT EXISTS idx_loans_returned_date ON loans(returned_date);
