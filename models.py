from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


def _parse_date(value: Optional[str]) -> Optional[date]:
    """Parse a stored 'YYYY-MM-DD' string into a date, or None."""
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


@dataclass
class Member:
    member_id: int
    full_name: str
    email: str
    phone: str = ""
    active: bool = True

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Member":
        keys = row.keys()
        return cls(
            member_id=row["id"],
            full_name=row["name"],
            email=row["email"],
            phone=row["phone"] or "" if "phone" in keys else "",
            active=bool(row["active"]) if "active" in keys else True,
        )

    @property
    def status_label(self) -> str:
        return "Active" if self.active else "Inactive"

    def __str__(self) -> str:
        return f"Member({self.member_id}, {self.full_name}, {self.email}, {self.phone})"


@dataclass
class Equipment:
    equipment_id: int
    name: str
    category: str = "General"
    item_condition: str = "Good"
    description: str = ""
    is_available: bool = True

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Equipment":
        keys = row.keys()
        return cls(
            equipment_id=row["id"],
            name=row["name"],
            category=(row["category"] or "General") if "category" in keys else "General",
            item_condition=(row["condition"] or "Good") if "condition" in keys else "Good",
            description=(row["description"] or "") if "description" in keys else "",
            is_available=bool(row["available"]),
        )

    @property
    def status_label(self) -> str:
        return "Available" if self.is_available else "Checked out"

    def __str__(self) -> str:
        return (
            f"Equipment({self.equipment_id}, {self.name}, {self.category}, "
            f"{self.item_condition}, Available: {self.is_available})"
        )


@dataclass
class Loan:
    loan_id: int
    member_id: int
    equipment_id: int
    checkout_date: Optional[date]
    due_date: Optional[date]
    returned_date: Optional[date] = None
    token: str = ""
    # Populated only when the row came from a joined query
    # (e.g. database.list_open_loans() / list_loans_with_names()).
    member_name: str = ""
    equipment_name: str = ""

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Loan":
        keys = row.keys()
        return cls(
            loan_id=row["id"],
            member_id=row["member_id"],
            equipment_id=row["equipment_id"],
            checkout_date=_parse_date(row["loan_date"]),
            due_date=_parse_date(row["due_date"]),
            returned_date=_parse_date(row["return_date"]),
            token=(row["token"] or "") if "token" in keys else "",
            member_name=row["member_name"] if "member_name" in keys else "",
            equipment_name=row["equipment_name"] if "equipment_name" in keys else "",
        )

    @property
    def is_open(self) -> bool:
        """True while the item hasn't been returned yet."""
        return self.returned_date is None

    def is_overdue(self, as_of: Optional[date] = None) -> bool:
        """True if still checked out and past its due date."""
        as_of = as_of or date.today()
        return self.is_open and self.due_date is not None and self.due_date < as_of

    def days_overdue(self, as_of: Optional[date] = None) -> int:
        """How many days overdue this loan is (0 if not overdue)."""
        as_of = as_of or date.today()
        if not self.is_open or self.due_date is None or self.due_date >= as_of:
            return 0
        return (as_of - self.due_date).days

    @property
    def status_label(self) -> str:
        if not self.is_open:
            return "Returned"
        return "OVERDUE" if self.is_overdue() else "Checked out"

    def __str__(self) -> str:
        return (
            f"Loan({self.loan_id}, Member ID: {self.member_id}, Equipment ID: {self.equipment_id}, "
            f"Checkout: {self.checkout_date}, Due: {self.due_date}, Returned: {self.returned_date})"
        )