# Campus MakerSpace Checkout System

A menu-driven Python application for managing MakerSpace members, equipment, and equipment loans. The application will store its data in a local SQLite database so records persist between runs.

> **Assessment repository:** This project is being developed for the BSc (Hons) Software Engineering module *Introduction to Programming and Databases* (August–October 2026).

## Project status

This repository is intentionally set up as a design-and-implementation starter. Complete each item below yourself and make sure you can explain every part during the live demonstration.

- [x] Repository layout and initial database design
- [ ] Implement domain classes in `models.py`
- [ ] Implement database connection and SQL helpers in `database.py`
- [ ] Implement checkout/return business rules in `services.py`
- [ ] Implement the menu and input validation in `main.py`
- [ ] Test all menu paths with sample data

## Planned features

1. Register, list, and update members.
2. Register, list, and update equipment, including its availability.
3. Check out equipment only when the member exists and the item is available.
4. Return a loan and update the equipment availability.
5. Search for a member or an equipment item by name or ID.
6. Run at least two reports: current loans, overdue loans, equipment by category, or member loan history.

## Project structure

```text
.
├── main.py          # Menu loop and application entry point
├── models.py        # Member, Equipment, and Loan classes
├── database.py      # SQLite connection, schema setup, and SQL helpers
├── services.py      # Business rules coordinating models and database
├── schema.sql       # Initial SQLite table design
├── README.md        # Setup, design, and assessment notes
└── .gitignore       # Excludes local database and temporary files
```

## Design overview

### Classes

| Class | Responsibility | Example behaviour to implement |
| --- | --- | --- |
| `Member` | Represents a MakerSpace member. | Validate or format member details. |
| `Equipment` | Represents an inventory item. | Check whether the item is available. |
| `Loan` | Represents a checkout transaction. | Determine whether a loan is overdue. |

### Database tables

- `members`: one record per member.
- `equipment`: one record per lendable item, with a category and availability status.
- `loans`: one record per checkout, linked to a member and an equipment item by foreign keys.

The starting schema is in `schema.sql`. The eventual application should create the database automatically on its first run or clearly document how to run the schema.

## Running the application

The intended final program uses only Python's standard library, including `sqlite3`, so no package installation should be necessary.

```bash
python3 main.py
```

## Suggested implementation order

1. Read `schema.sql` and draw a quick relationship diagram: one member can have many loans; one equipment item can have many loans over time.
2. Build the three domain classes and give each meaningful methods.
3. Add database setup and simple member/equipment CRUD operations.
4. Add checkout and return operations, including validation.
5. Add search and reports, then test invalid input and edge cases.
6. Commit small, meaningful milestones to GitHub.

## GitHub submission checklist

- [ ] Rename the repository to `Lab_MakerSpace_<your-GitHub-username>` if needed.
- [ ] Keep source files, `schema.sql`, and this README committed.
- [ ] Do **not** commit `makerspace.db` unless your lecturer explicitly asks for a populated database file.
- [ ] Add clear comments only where they explain a design decision or non-obvious logic.
- [ ] Make sure the project runs from a fresh clone.
- [ ] Submit the public repository link on Canvas and be ready to explain the code live.

## AI-use acknowledgement

Generative AI was used as a learning and setup aid to organise the initial repository structure, outline the SQLite schema, and improve this documentation. All final implementation code is reviewed, understood, tested, and explained by the student. Update this statement to accurately reflect any further assistance used.

## References

Add any external sources or adapted snippets here in APA 7 style, with links. Include a short code comment next to each adapted snippet explaining its source.
