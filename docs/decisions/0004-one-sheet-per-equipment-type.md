# 0004: One sheet per equipment type; users add rows in Excel

- **Status:** accepted
- **Date:** 2026-11-08
- **Amends:** [0001](0001-shared-24-column-grid.md), which put every table on one sheet

## Context
A schedule needs as many rows as the project has items: two generators on one job,
forty disconnects on another. Empty spare rows must not end up on drawings. The workbook
has no macros (NFR-01), so it can't add rows by itself: every formula has to exist in
a cell before the user needs it. With all tables stacked on one sheet, a table also
can't grow without running into the one below it.

## Options considered
1. **All tables on one sheet with a fixed number of rows each.** Simple, but either too
   few rows or stray empty ones, and growing a table means moving the others.
2. **One sheet per type, using Excel Tables.** Tables grow automatically as you type below
   them and copy formulas down. But Excel Tables cannot contain merged cells, and the
   grid (ADR 0001) relies on merges for fields that span several columns.
3. **One sheet per type, plain ranges; users add rows with *Insert Copied Cells*.**
   Copying an existing row and inserting it brings its merges, borders and formulas
   with it. Native Excel, no macros.

## Decision
Option 3. Each equipment type gets its own sheet with identical column widths, so the
tables still line up when pasted into a drawing. A schedule starts with a few rows
(`start_rows` in `layout.yaml`). To add one: select a data row, copy, then select the
**last** data row and choose *Insert Copied Cells*, which inserts *above* it, inside the
table, so the named range (`SCH_<TYPE>`) grows with it. Unused rows are deleted.

## Consequences
- No stray rows, and no limit beyond what the user adds.
- One table per sheet also ends page splits between tables (REQ-05).
- Users need a one-line instruction for adding rows; it goes on each sheet (M4).
- Rows inserted *below* the last row fall outside the named range. To check in the pilot:
  does that happen in practice, and is the instruction enough?
- If a future version drops merged cells (for example, using *Center Across Selection*),
  option 2 becomes possible and this decision should be revisited.
