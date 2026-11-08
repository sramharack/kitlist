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
| REQ-05 | Each schedule sheet prints landscape, fit to page width. | done (M3) | `test_writer.py` |
| REQ-06 | Equipment is sized as the smallest standard size covering load plus spare. The spare margin is always stated explicitly. | Python done; Excel in M4 | `test_sizing.py` |
| REQ-07 | Each row is checked against engineering rules; problems are shown beside the row. First rule: a generator prime rating above standby is an error; prime equal to standby is allowed, with a note to confirm on the manufacturer's datasheet (D5). | in progress (M0 exercise) | `test_checks.py` |
| REQ-08 | Project defaults (system voltages, frequency, indoor/outdoor enclosure) are entered once on a Project sheet. | M4 | |
| REQ-09 | Branding comes from a profile file passed to the build; the public build carries no company branding. | M4 | |
| REQ-10 | Each equipment type has its own sheet, with the same column widths on every sheet. A schedule starts with a few rows; users add rows with Excel's *Insert Copied Cells* and delete unused ones, so no stray rows are left (D6, ADR 0004). | done (M3); row insertion to be checked in pilot | `test_writer.py` |
| REQ-11 | Transformer sizes are selected only from the rating family chosen for each item (`ieee-dry`, `ieee-pad` or `iec`); families are never mixed (D7). | M3 | `test_library.py` (planned) |

## Non-functional requirements

| ID | Requirement |
|---|---|
| NFR-01 | No macros. Excel-2007-era functions only. Works in desktop Excel, Excel online and LibreOffice. |
| NFR-02 | The workbook is self-contained: no links to other files. |
| NFR-03 | Every engineering rule has Python tests, and an automated test checks the Excel formula agrees with Python (ADR 0002). |
| NFR-04 | A schedule shows what a drawing needs: at most about 7 ratings per type. Detail belongs in the specification. |
| NFR-05 | Every value in an equipment library cites a source listed in `docs/design-basis.md`. A test fails if a source is missing or unlisted. |

## Non-goals (v0.1)

- Writing specifications.
- A manufacturer product database. Libraries hold standard sizes and typical dimensions only.
- Load calculations. Demand is an input, calculated elsewhere.
- Certifying compliance with standards. Library sizes come from the cited standards; whether a product complies is confirmed by the manufacturer's data.
- DXF/PDF output, AutoCAD Data Link and native AutoCAD table objects. v0.1 gets schedules into drawings by copy-paste; the rest comes later.

## Decisions

Engineering decisions behind the layout and libraries. D1–D3 are pinned by tests
(`test_grid.py`, names starting `test_d1_` etc.), so they can't change by accident;
changing one means changing its test on purpose, in a reviewed pull request.

| # | Question | Decision | Why |
|---|---|---|---|
| D1 | Dimensions in inches or mm? | Inches. | Matches the office's existing schedules. Could become a profile setting later. |
| D2 | Show "provisional" on the schedule? | Yes: the group header reads PROVISIONAL DIMENSIONS. | Exact dimensions often aren't known at design stage; typical sizes stand in for them. |
| D3 | Generator ratings in kW or kVA? | kVA, for standby and prime ratings. | Demand served (a load) is in kVA; ratings in the same unit compare directly, with no hidden power factor. |
| D4 | Where do generator enclosure and fuel type go? | The specification, not the schedule. | They're requirements, not ratings (NFR-04). |
| D5 | Is prime rating equal to standby acceptable? | Yes, with a note to confirm on the manufacturer's datasheet. Prime above standby is an error. | Some manufacturers (e.g. CAT) rate some units with prime equal to standby. |
| D6 | How many rows per table? | As many as the user needs: one sheet per type; rows added or deleted in Excel. | No stray empty rows on drawings (ADR 0004). |
| D7 | Which transformer rating series? | Three families: IEEE dry-type (LV), IEEE liquid-filled padmount, and IEC. The selector picks only within the family chosen for each item. | Projects use US and European equipment on a 50 Hz supply; mixing series in one list would select sizes the chosen supplier doesn't make. |

## Open questions

| # | Question | Notes |
|---|---|---|
| Q8 | Do padmount transformers get their own schedule? | Padmount purchases usually state primary voltage, BIL, loop or radial feed, fluid and impedance, which the dry-type schedule doesn't have. Check what IEEE C57.12.34 asks the purchaser to specify. |