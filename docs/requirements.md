# Requirements (v0.1)

Each requirement has an ID. Tests name the requirement they check (e.g. `# REQ-01`),
so you can trace any requirement to the test that proves it, and any test back to why
it exists.

## Users

- **Office engineers** use the workbook. They have Excel, not Python.
- **Maintainers** (initially one) change the code, layout and libraries in the repo.

## Functional requirements

| ID | Requirement | Status | Verified by |
|---|---|---|---|
| REQ-01 | Every schedule uses one shared grid: each table is full width, and Tag, Description, Qty, Dimensions and Notes sit in the same columns in every table. | done (M2) | `test_grid.py`, `test_writer.py` |
| REQ-02 | The layout is defined in one data file (`layout.yaml`). An invalid layout is rejected with a message naming the equipment type and the problem. | done (M2) | `test_grid.py` |
| REQ-03 | Each table has a title row, a group row, a field-label row and a unit row; units are shown in square brackets. | done (M2) | `test_grid.py` |
| REQ-04 | Each table is a named range (`SCH_<TYPE>`), so it can be selected in one step (Name Box) and copy-pasted into AutoCAD. v0.1 relies on manual copy-paste; AutoCAD Data Link and native table objects come after v0.1, using the same named ranges. | done (M2), paste trial pending | `test_writer.py` |
| REQ-05 | The schedules sheet prints landscape, fit to page width. Tables are not split across pages. | partial: page splits open | `test_writer.py` |
| REQ-06 | Equipment is sized as the smallest standard size covering load plus spare. | Python done; Excel in M4 | `test_sizing.py` |
| REQ-07 | Each row is checked against engineering rules; problems are shown beside the row. First rule: generator prime rating ≤ standby rating. | in progress (M0 exercise) | `test_checks.py` |
| REQ-08 | Project defaults (system voltages, frequency, indoor/outdoor enclosure) are entered once on a Project sheet. | M4 | |
| REQ-09 | Branding comes from a profile file passed to the build; the public build carries no company branding. | M4 | |

## Non-functional requirements

| ID | Requirement |
|---|---|
| NFR-01 | No macros. Excel-2007-era functions only. Works in desktop Excel, Excel online and LibreOffice. |
| NFR-02 | The workbook is self-contained: no links to other files. |
| NFR-03 | Every engineering rule has Python tests, and an automated test checks the Excel formula agrees with Python (ADR 0002). |
| NFR-04 | A schedule shows what a drawing needs: at most about 7 ratings per type. Detail belongs in the specification. |

## Non-goals (v0.1)

- Writing specifications.
- A manufacturer product database. Libraries hold standard sizes and typical dimensions only.
- Load calculations. Demand is an input, calculated elsewhere.
- DXF/PDF output, AutoCAD Data Link and native AutoCAD table objects. v0.1 gets schedules into drawings by copy-paste; the rest comes later.

## Open questions

These are engineering calls, not coding ones. Each is marked `DECIDE` in `layout.yaml`.

| # | Question | Notes |
|---|---|---|
| Q1 | Dimensions in inches or mm? | Sample schedules use inches. Could be a profile default. |
| Q2 | Is "provisional" shown on the schedule or in a general note? | Shown on the schedule as exact dimensions are not always known and may need be proxied |
| Q3 | Generator ratings in kW or kVA? | Demand served is load not the unit size
| Q4 | Where do generator enclosure and fuel type go? | This will be deffered to the specification document. |
| Q5 | Is prime rating equal to standby rating acceptable? | No, this does vary on manufacturer such as CAT however, as these units prime is the same as standby
| Q6 | How many data rows per table, and how are unused rows hidden? | Unlimited |
