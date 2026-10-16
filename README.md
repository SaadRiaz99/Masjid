# DRAIE - Disaster Resource Allocator & Inventory Engine

A desktop application for tracking disaster-relief resources, the regions you
serve, and the allocations you dispatch to them.

The UI is built with tkinter (no extra dependencies), the data lives in
plain CSV files, and the code is split into classic layers so each one stays
small and easy to read.

## Getting started

```bash
uv sync                 # or just use any Python 3.14 interpreter
python main.py          # launch the desktop app
```

Other ways to start it:

```bash
python -m src.presentation.app
python dashboard.py
softwarre               # console script installed by uv
```

## Running the tests

The tests use `unittest` from the standard library:

```bash
python -m unittest discover -v
```

## Project layout

```
data/                    CSV tables (the whole database)
src/
  models/                Domain objects + validation
  data_access/           CSV reading/writing
  business/              Business rules and permissions
  presentation/          tkinter UI (app shell, views, widgets, backend)
tests/                   unittest test suite
main.py                  App entry point
```

Data flows in one direction: **presentation → business → data access → CSV**.

- `src/models` - `Resource`, `Region`, `Allocation`, `User`. Each model knows
  how to validate itself and how to map to/from a CSV row. A resource's
  `status` (`In Stock` / `Low` / `Out of Stock`) is always derived from its
  quantity and reorder level, never typed in by hand.
- `src/data_access` - `CsvStore` reads and writes one CSV file, `Database`
  bundles the four tables. Writes are atomic (temp file + rename).
- `src/business` - the services that enforce the rules: unique names,
  existing references, valid dates, permissions, and stock movements.
- `src/presentation` - `app.py` is the window with the sidebar, `views/` are
  the five screens, `widgets.py` holds the reusable table/dialog/base view,
  and `backend.py` is the single place where the UI is wired to the services.

## The backend

The UI only talks to the interface declared in `src/presentation/backend.py`.
`get_backend()` returns a `CsvBackend`, which connects the CSV tables to the
business services. To use a different storage engine, subclass `Backend`,
implement the same methods, and return your class from `get_backend()`.

## Roles and permissions

| Action            | Admin | Manager | Coordinator | Viewer |
|-------------------|:-----:|:-------:|:-----------:|:------:|
| View everything   |  yes  |   yes   |     yes     |  yes   |
| Manage inventory  |  yes  |   yes   | own region  |   -    |
| Manage regions    |  yes  | create/edit |   -    |   -    |
| Manage allocations|  yes  |   yes   | own region  |   -    |
| Manage users      |  yes  |    -    |      -      |   -    |

Coordinators are limited to their own region: they only see resources and
allocations for the region named on their user record.

## Business rules worth knowing

- Resource names and region names are unique (case-insensitive), so
  allocations can refer to them by name.
- An allocation holds stock while it is active (`Pending`, `Approved`,
  `In Transit`, `Delivered`). Creating one deducts stock; cancelling or
  deleting it gives the stock back; editing the quantity moves the
  difference.
- Stock status is derived: `quantity <= 0` is *Out of Stock*,
  `quantity <= reorder_level` is *Low*, otherwise *In Stock*.
- Dates must be `YYYY-MM-DD`.

## Data

The four tables in `data/` ship with sample data:

| File               | Columns                                                    |
|--------------------|------------------------------------------------------------|
| `resources.csv`    | id, name, category, quantity, unit, region, reorder_level, status |
| `regions.csv`      | id, name, district, coordinator, population, risk_level    |
| `allocations.csv`  | id, resource, region, quantity, priority, date, status     |
| `users.csv`        | id, name, username, role, region, status                   |

Delete the files to start from scratch - they are recreated with headers the
next time the app runs.
