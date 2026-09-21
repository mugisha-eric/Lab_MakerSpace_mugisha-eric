# Campus MakerSpace Checkout System

An interactive command-line app for running a campus makerspace's front desk for 
registering members and equipment, checking items in and out, tracking overdue loans,
and pulling reports, all from an interactive colored, arrow-key-navigable terminal UI.

## Features

- **Arrow-key menu** (via `questionary`), with a plain numbered fallback if it isn't installed
- **Command palette** — type a word like `checkout`, `return`, or `search drill` instead of a menu number
- **Color-coded dashboard** — a `rich` table view showing equipment as Available / Checked out / **OVERDUE**
- **Overdue alerts** shown automatically the moment the app opens
- **Checkout tokens** — every loan gets a short, memorable ticket like `LOAN-7F2K` instead of a raw database ID
- **Cancel anywhere** — type `cancel`, `back`, `esc`, or `:q` at any prompt to back out of what you're doing
- **Confirmation prompts** before registering, deleting, or undoing anything
- **Duplicate checks** — won't register a member with an email already on file, or equipment with a name already in use
- **One-step Undo** for the last create action (register member, register equipment, checkout)
- **Delete member / delete equipment**, with a confirmation step
- **Three built-in reports** — Operation Status, Health & Condition, and Utilization
- **Fuzzy search** — typo-tolerant matching against member and equipment names
- **Persistent storage** via SQLite (`makerspace.db`), so data survives restarts
- **Screen clears after every action**, right before the menu redraws, so the terminal doesn't get cluttered

## Requirements

- Python 3.10+
- Optional, for the full interactive experience:
  - [`rich`](https://github.com/Textualize/rich) — color output, tables, panels
  - [`questionary`](https://github.com/tmbo/questionary) — arrow-key menu navigation

Without these two packages the app still runs in full, just in a plain-text
fallback mode (numbered menus, no color).

## Installation

```bash
git clone https://github.com/mugisha-eric/Lab_MakerSpace_mugisha-eric.git
cd Lab_MakerSpace_mugisha-eric
pip install -r requirements.txt
```


## Running the app

```bash
python3 main.py
```

On first run, `main.py` calls `database.create_tables()`, which creates
`makerspace.db` in the current directory if it doesn't already exist. No
manual setup is required.

## Project structure

```
.
├── main.py             # Interactive CLI — menu, prompts, dashboard, reports
├── database.py          # SQLite connection, schema, and parameterized queries
├── models.py             # Member / Equipment / Loan domain objects
├── requirements.txt
└── makerspace.db          # created automatically on first run (not checked in)
```


`main.py` never writes raw SQL, and `database.py` never formats anything for
display — each layer only talks to the one below it.

## Main menu

| # | Option | Description |
|---|---|---|
| 1 | Register Member | Add a new member. Rejects duplicate emails. |
| 2 | List Members | Display all members with status (Active/Inactive). |
| 3 | Update Member | Edit an existing member's details. |
| 4 | Delete Member | Remove a member, after confirmation. |
| 5 | Register Equipment | Add new equipment. Rejects duplicate names. |
| 6 | List Equipment | Display Colored table of equipment: green = available, yellow = checked out, red = **OVERDUE**. |
| 7 | Update Equipment | Edit an existing item's details. |
| 8 | Delete Equipment | Remove an item, after confirmation. |
| 9 | Create Loan (Checkout) | Pick a member and an available item and select custom or default due date. |
| 10 | Return Loan | Pick an open loan to close out and free up the equipment. |
| 11 | Operation Status Report | Quick counts: total members, total equipment, open loans, overdue loans. |
| 12 | Health and Condition Report | Equipment grouped by condition (Good / Needs Repair / etc.), with counts. |
| 13 | Utilization Report | How many times each piece of equipment has been borrowed. |
| `undo` | Undo Last Action | Reverses the most recent register/checkout, with a confirmation prompt. |
| `0` | Exit | Closes the database connection and quits. |


### Canceling out of a prompt

Type `cancel`, `back`, `esc`, or `:q` at any text prompt (member name, email,
equipment description, etc.) to back out. Use `Ctrl + C` to go back when there is no input option. 

# Design overview

## Classes

| Class | Responsibility |
| --- | --- |
| `Member` | Represents a MakerSpace member. |
| `Equipment` | Represents an inventory item. |
| `Loan` | Represents a checkout transaction. |


## Data model

### Member
| Field | Type |
|---|---|
| `member_id` | int |
| `full_name` | str |
| `email` | str |
| `phone` | str |
| `active` | bool |

### Equipment
| Field | Type |
|---|---|
| `equipment_id` | int |
| `name` | str |
| `category` | str |`"General"` |
| `item_condition` | str |
| `description` | str |
| `is_available` | bool |

### Loan
| Field | Type |
|---|---|
| `loan_id` | int |
| `token` | str |
| `member_id` / `equipment_id` | int |
| `checkout_date` / `due_date` | date |(`LOAN_PERIOD_DAYS`) |
| `returned_date` | date or None |


## Reports

- **Operation Status Report** — a snapshot: how many members, how much equipment,
  how many open loans, how many are currently overdue.
- **Health and Condition Report** — equipment grouped and counted by `item_condition`,
  useful for spotting how much gear needs repair or replacement.
- **Utilization Report** — how many times each item has ever been borrowed, to see
  what's getting the most (or least) use.


## AI-use acknowledgement

Generative AI was used as a learning and setup aid to organise the initial repository structure, outline the `SQLite` schema, and improve this documentation. All final implementation code is orginally written, reviewed, understood, tested, and explained by the student.
