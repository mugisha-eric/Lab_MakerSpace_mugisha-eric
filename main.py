"""
Campus MakerSpace Checkout System — an interactive CLI.

"""

from __future__ import annotations

import csv
import difflib
import hashlib
import os
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Callable, Optional

import database as db
from models import Equipment, Loan, Member

# ---------------------------------------------------------------------------
# Optional pretty UI. Everything still works without these installed.
# ---------------------------------------------------------------------------
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    from rich import box

    console: Optional[Console] = Console() # type: ignore
    RICH_OK = True
except ImportError:
    Console = Table = Panel = Prompt = Confirm = box = None  # type: ignore[assignment,misc]
    console = None
    RICH_OK = False

try:
    import questionary

    QUESTIONARY_OK = True
except ImportError:
    questionary = None  # type: ignore[assignment]
    QUESTIONARY_OK = False

LOAN_PERIOD_DAYS = 7

CANCEL_TOKENS = {"cancel", "back", "esc", ":q"}

    

# ---------------------------------------------------------------------------
# Small output helpers so the rest of the code doesn't care which libs exist
# ---------------------------------------------------------------------------
def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def say(msg: str, style: str = "") -> None:
    if console is not None:
        console.print(msg, style=style or None)
    else:
        print(msg)


def banner(text: str, style: str = "bold cyan") -> None:
    if console is not None and Panel is not None:
        console.print(Panel.fit(text, border_style=style))
    else:
        print(f"\n=== {text} ===")


def show_table(title: str, columns: list[str], rows: list[list[str]], row_styles: Optional[list[str]] = None) -> None:
    if console is not None and Table is not None and box is not None:
        table = Table(title=title, box=box.ROUNDED, show_lines=False)
        for col in columns:
            table.add_column(col)
        for i, row in enumerate(rows):
            style = row_styles[i] if row_styles else None
            table.add_row(*row, style=style)
        console.print(table)
    else:
        print(f"\n-- {title} --")
        print(" | ".join(columns))
        for row in rows:
            print(" | ".join(row))


def ask(prompt: str, default: str = "") -> str:
    if RICH_OK and Prompt is not None:
        val = Prompt.ask(prompt, default=default or None) or ""
    else:
        raw = input(f"{prompt}{f' [{default}]' if default else ''}: ")
        val = raw or default
    if val.strip().lower() in CANCEL_TOKENS:
        say("Action cancelled.", "yellow")
        input("\nPress Enter to return to the main menu...")
        os.system("cls" if os.name == "nt" else "clear")
        main()  # Restart the main menu if the user cancels
    return val


def confirm(prompt: str) -> bool:
    if RICH_OK and Confirm is not None:
        return Confirm.ask(prompt)
    return input(f"{prompt} (y/n): ").strip().lower().startswith("y")


def pick(prompt: str, choices: list[str]) -> Optional[str]:
    """Arrow-key select if questionary is available, else numbered fallback."""
    if not choices:
        say("Nothing to choose from.", "yellow")
        return None
    if QUESTIONARY_OK and questionary is not None:
        return questionary.select(prompt, choices=choices).ask()
    print(prompt)
    for i, c in enumerate(choices, 1):
        print(f"  {i}. {c}")
    idx = ask("Enter number")
    try:
        return choices[int(idx) - 1]
    except (ValueError, IndexError):
        return None


# ---------------------------------------------------------------------------
# Undo support — stores a single reversible action
# ---------------------------------------------------------------------------
@dataclass
class UndoAction:
    description: str
    undo_fn: Callable[[], None]


class UndoStack:
    def __init__(self) -> None:
        self._last: Optional[UndoAction] = None

    def push(self, description: str, undo_fn: Callable[[], None]) -> None:
        self._last = UndoAction(description, undo_fn)

    def undo(self) -> None:
        if not self._last:
            say("Nothing to undo.", "yellow")
            return
        else:
            if not confirm(f"Undo last action: {self._last.description}?"):
                say("Undo cancelled.", "yellow")
                return
            self._last.undo_fn()
            say(f"Undone: {self._last.description}", "green")
            self._last = None


# ---------------------------------------------------------------------------
# Checkout token — short, memorable, unique-enough for a claim ticket
# ---------------------------------------------------------------------------
def make_token(member_id: int, equipment_id: int) -> str:
    seed = f"{member_id}-{equipment_id}-{datetime.now().timestamp()}"
    digest = hashlib.sha1(seed.encode()).hexdigest().upper()
    return f"LOAN-{digest[:4]}"


# ---------------------------------------------------------------------------
# Main application
# ---------------------------------------------------------------------------
class MakerSpaceApp:
    def __init__(self) -> None:
        db.create_tables()
        self.undo = UndoStack()

    # -- Members -----------------------------------------------------------
    def register_member(self) -> None:
        banner("Register Member")
        name = ask("Member full name")
        email = ask("Email")
        phone = ask("Phone (optional)", default="")
        if not name or not email:
            say("Name and email are required.", "red")
            return
        elif db.search_members_by_email(email):
                say(f"A member with email {email} already exists.", "red")
                return
        elif not confirm(f"Register {name} with email {email}?"):
            say("Registration cancelled.", "yellow")
            return
        member_id = db.add_member(name, email, phone)

        def _undo():
            db.delete_member(member_id)

        self.undo.push(f"register member '{name}'", _undo)
        say(f"Registered {name} (id {member_id})", "green")

    def list_members(self) -> None:
        members = [Member.from_row(r) for r in db.list_members()]
        show_table(
            "Members",
            ["ID", "Name", "Email", "Phone", "Status"],
            [[str(m.member_id), m.full_name, m.email, m.phone or "-", m.status_label] for m in members],
        )

    def update_member(self) -> None:
        banner("Update Member")
        member = self._select_member()
        if not member:
            return
        name = ask("New name", default=member.full_name)
        email = ask("New email", default=member.email)
        phone = ask("New phone", default=member.phone)
        db.update_member(member.member_id, name, email, phone)
        say("Member updated.", "green")

    def delete_member(self) -> None:
        banner("Delete Member")
        member = self._select_member()
        if not member:
            return
        if confirm(f"Are you sure you want to delete {member.full_name}?"):
            db.delete_member(member.member_id)
            say(f"Deleted {member.full_name}.", "green")
        else:
            say("Deletion cancelled.", "yellow")

    def generate_operation_status_report(self) -> None:
        banner("Operation Status Report")
        members = [Member.from_row(r) for r in db.list_members()]
        equipment = [Equipment.from_row(r) for r in db.list_equipment()]
        open_loans = [Loan.from_row(r) for r in db.list_open_loans()]
        overdue_loans = [l for l in open_loans if l.is_overdue()]

        say(f"Total members: {len(members)}")
        say(f"Total equipment: {len(equipment)}")
        say(f"Open loans: {len(open_loans)}")
        say(f"Overdue loans: {len(overdue_loans)}")

    def _select_member(self) -> Optional[Member]:
        members = [Member.from_row(r) for r in db.list_members()]
        if not members:
            say("No members yet.", "yellow")
            return None
        labels = [f"{m.member_id}: {m.full_name} ({m.email})" for m in members]
        choice = pick("Select a member", labels)
        if not choice:
            return None
        member_id = int(choice.split(":")[0])
        return next(m for m in members if m.member_id == member_id)

    # -- Equipment -----------------------------------------------------------
    def register_equipment(self) -> None:
        banner("Register Equipment")
        name = ask("Equipment name")
        category = ask("Category", default="General")
        condition = ask("Condition", default="Good")
        description = ask("Description (optional)", default="")

        if not name:
            say("Equipment name is required.", "red")
            return
        elif db.search_equipment_by_name(name):
            say(f"Equipment with name '{name}' already exists.", "red")
            return
        elif not confirm(f"Register {name} in category '{category}' with condition '{condition}'?"):
            say("Registration cancelled.", "yellow")
            return
        equipment_id = db.add_equipment(name, category, description, condition)

        def _undo():
            db.delete_equipment(equipment_id)

        self.undo.push(f"register equipment '{name}'", _undo)
        say(f"Registered {name} (id {equipment_id})", "green")

    def list_equipment(self) -> None:
        equipment = [Equipment.from_row(r) for r in db.list_equipment()]
        overdue_ids = self._overdue_equipment_ids()
        styles, table_rows = [], []
        for e in equipment:
            if e.is_available:
                status, style = "Available", "green"
            elif e.equipment_id in overdue_ids:
                status, style = "OVERDUE", "bold red"
            else:
                status, style = "Checked out", "yellow"
            table_rows.append([str(e.equipment_id), e.name, e.category, e.item_condition, status])
            styles.append(style)
        show_table("Equipment", ["ID", "Name", "Category", "Condition", "Status"], table_rows, styles)

    def update_equipment(self) -> None:
        banner("Update Equipment")
        eq = self._select_equipment(only_any=True)
        if not eq:
            return
        name = ask("New name", default=eq.name)
        category = ask("New category", default=eq.category)
        condition = ask("New condition", default=eq.item_condition)
        description = ask("New description", default=eq.description)
        db.update_equipment(eq.equipment_id, name, category, description, condition)
        say("Equipment updated.", "green")

    def delete_equipment(self) -> None:
        banner("Delete Equipment")
        eq = self._select_equipment(only_any=True)
        if not eq:
            return
        if confirm(f"Are you sure you want to delete {eq.name}?"):
            db.delete_equipment(eq.equipment_id)
            say(f"Deleted {eq.name}.", "green")
        else:
            say("Deletion cancelled.", "yellow")

    def generate_health_condition_report(self) -> None:
        banner("Health and Condition Report")
        equipment = [Equipment.from_row(r) for r in db.list_equipment()]
        condition_counts: dict[str, int] = {}
        for e in equipment:
            condition_counts[e.item_condition] = condition_counts.get(e.item_condition, 0) + 1
        show_table(
            "Equipment Condition Summary",
            ["Condition", "Count"],
            [[cond, str(count)] for cond, count in condition_counts.items()],
        )

    def generate_utilization_report(self) -> None:
        banner("Utilization Report")
        equipment = [Equipment.from_row(r) for r in db.list_equipment()]
        utilization_counts: dict[str, int] = {}
        for e in equipment:
            utilization_counts[e.name] = db.get_loan_count_for_equipment(e.equipment_id)
        show_table(
            "Equipment Utilization Summary",
            ["Equipment", "Times Borrowed"],
            [[name, str(count)] for name, count in utilization_counts.items()],
        )

    def _select_equipment(self, only_available: bool = False, only_any: bool = False) -> Optional[Equipment]:
        rows = db.list_available_equipment() if only_available else db.list_equipment()
        equipment = [Equipment.from_row(r) for r in rows]
        if not equipment:
            say("No matching equipment.", "yellow")
            return None
        labels = [f"{e.equipment_id}: {e.name} ({e.category})" for e in equipment]
        choice = pick("Select equipment", labels)
        if not choice:
            return None
        eq_id = int(choice.split(":")[0])
        return next(e for e in equipment if e.equipment_id == eq_id)

    # -- Loans -----------------------------------------------------------
    def create_loan(self) -> None:
        banner("Checkout Equipment")
        member = self._select_member()
        if not member:
            return
        equipment = self._select_equipment(only_available=True)
        if not equipment:
            say("No available equipment to check out.", "yellow")
            return

        token = make_token(member.member_id, equipment.equipment_id)
        checkout = date.today()
        due = checkout + timedelta(days=LOAN_PERIOD_DAYS)

        loan_id = db.create_loan(member.member_id, equipment.equipment_id, checkout.isoformat(), due.isoformat(), token)
        db.set_equipment_availability(equipment.equipment_id, False)

        def _undo():
            db.delete_loan(loan_id)
            db.set_equipment_availability(equipment.equipment_id, True)

        self.undo.push(f"checkout of '{equipment.name}'", _undo)

        banner(f"{token}", "bold green")
        say(f"{member.full_name} checked out {equipment.name}. Due back {due.isoformat()}.")

    def return_loan(self) -> None:
        banner("Return Equipment")
        open_loans = [Loan.from_row(r) for r in db.list_open_loans()]
        if not open_loans:
            say("No active loans.", "yellow")
            return
        labels = [f"{l.token}: {l.equipment_name} — {l.member_name}" for l in open_loans]
        choice = pick("Select the loan to return", labels)
        if not choice:
            return
        token = choice.split(":")[0]
        loan = next(l for l in open_loans if l.token == token)

        db.close_loan(loan.loan_id, date.today().isoformat())
        db.set_equipment_availability(loan.equipment_id, True)
        say(f"{loan.equipment_name} returned by {loan.member_name}.", "green")

    def _overdue_equipment_ids(self) -> set[int]:
        loans = [Loan.from_row(r) for r in db.get_overdue_loans(date.today().isoformat())]
        return {l.equipment_id for l in loans}

    def _overdue_count(self) -> int:
        return len(self._overdue_equipment_ids())

    # -- Reports -----------------------------------------------------------
    def generate_reports(self) -> None:
        banner("Reports & Leaderboard")

        top_borrowers = db.get_top_borrowers(limit=5)
        show_table(
            "Top Borrowers",
            ["Rank", "Member", "Loans"],
            [[f"#{i+1}", r["name"], str(r["loan_count"])] for i, r in enumerate(top_borrowers)],
        )

        popular_equipment = db.get_popular_equipment(limit=5)
        show_table(
            "Most Popular Equipment",
            ["Rank", "Equipment", "Times Borrowed"],
            [[f"#{i+1}", r["name"], str(r["loan_count"])] for i, r in enumerate(popular_equipment)],
        )

        if confirm("Export full loan history to CSV?"):
            self._export_csv()

    def _export_csv(self) -> None:
        loans = [Loan.from_row(r) for r in db.list_loans_with_names()]
        out_path = Path("loan_report.csv")
        with out_path.open("w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Token", "Member", "Equipment", "Checkout", "Due", "Returned", "Status"])
            for l in loans:
                writer.writerow(
                    [l.token, l.member_name, l.equipment_name, l.checkout_date, l.due_date,
                     l.returned_date or "—", l.status_label]
                )
        say(f"Exported to {out_path.resolve()}", "green")

    # -- Fuzzy search helper -----------------------------------------------
    @staticmethod
    def _fuzzy(query: str, name_to_obj: dict):
        if not query:
            return list(name_to_obj.values())
        close = difflib.get_close_matches(query, name_to_obj.keys(), n=10, cutoff=0.3)
        # Also catch substring matches difflib might miss (e.g. short queries)
        substring = [n for n in name_to_obj if query.lower() in n.lower() and n not in close]
        return [name_to_obj[n] for n in close + substring]

    # -- Dashboard -----------------------------------------------------------
    def dashboard(self) -> None:
        overdue = self._overdue_count()
        if overdue:
            banner(f"{overdue} item(s) overdue right now", "bold red")

    def run(self) -> None:
        banner("Campus MakerSpace Checkout System", "bold cyan")
        say("Tip: type 'cancel', 'back', 'esc', ':q' to go back or pick from the menu.\n")

        commands = {
            "1": ("Register Member", self.register_member),
            "2": ("List Members", self.list_members),
            "3": ("Update Member", self.update_member),
            "4": ("Delete Member", self.delete_member),
            "5": ("Register Equipment", self.register_equipment),
            "6": ("List Equipment", self.list_equipment),
            "7": ("Update Equipment", self.update_equipment),
            "8": ("Delete Equipment", self.delete_equipment),
            "9": ("Create Loan (Checkout)", self.create_loan),
            "10": ("Return Loan", self.return_loan),
            "11": ("Operation Status Report", self.generate_operation_status_report),
            "12": ("Health and Condition Report", self.generate_health_condition_report),
            "13": ("Utilization Report", self.generate_utilization_report),
            "undo": ("Undo Last Action", self.undo.undo),
        }
        # Aliases so the "command palette" feel works with plain words too
        aliases = {
            "checkout": "9", "return": "10", "members": "2", "equipment": "5",
            "register member": "1", "register equipment": "4",
            "reports": "13", "search members": "11", "search equipment": "12",
        }

        while True:
            self.dashboard()
            if QUESTIONARY_OK and questionary is not None:
                labels = [f"{k}. {v[0]}" for k, v in commands.items() if k != "undo"]
                labels += ["undo. Undo Last Action", "0. Exit"]
                choice = questionary.select("Main Menu:", choices=labels).ask()
                if choice is None or choice.startswith("0"):
                    break
                key = choice.split(".")[0]
            else:
                say("\nMain Menu:")
                for k, (label, _) in commands.items():
                    if k != "undo":
                        say(f"{k}. {label}")
                say("undo. Undo Last Action")
                say("0. Exit")
                raw = ask("Select an option or type a command").strip().lower()
                if raw == "0":
                    break
                key = aliases.get(raw, raw)
                if raw.startswith("search "):
                    # e.g. "search drill" -> jump straight into equipment search with the term
                    term = raw[len("search "):]
                    equipment = [Equipment.from_row(r) for r in db.list_equipment()]
                    matches: list[Equipment] = self._fuzzy(term, {e.name: e for e in equipment})
                    show_table(f"Matches for '{term}'", ["ID", "Name", "Category"],
                               [[str(e.equipment_id), e.name, e.category] for e in matches])
                    input("\nPress Enter to return to the main menu...")
                    clear_screen()
                    continue

            action = commands.get(key)
            if action:
                action[1]()
            else:
                say("Unrecognized option.", "red")

            input("\nPress Enter to return to the main menu...")
            clear_screen()

        say("Goodbye!", "bold cyan")
        db.close_connection()


def main() -> None:
    if not RICH_OK or not QUESTIONARY_OK:
        missing = []
        if not RICH_OK:
            missing.append("rich")
        if not QUESTIONARY_OK:
            missing.append("questionary")
        print(f"(Running in plain-text mode — install {' and '.join(missing)} for the full interactive experience: "
              f"pip install {' '.join(missing)})\n")
    MakerSpaceApp().run()


if __name__ == "__main__":
    main()