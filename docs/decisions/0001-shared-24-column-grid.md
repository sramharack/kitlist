# 0001: All schedules share one 24-column grid

- **Status:** accepted
- **Date:** 2026-11-07

## Context
Each equipment schedule was a separate Excel range with its own column widths.
Stacked on a drawing, the tables had different overall widths and their columns
didn't line up. Pasted or linked into AutoCAD, the mismatch was obvious. Headers
also got truncated (e.g. "INCLOSURE RATIN") because widths were set by hand.

## Options considered
1. **Same columns for every schedule, unused ones left blank.** Simple, but tables
   with few fields look empty and those with many don't fit.
2. **Each schedule sized independently, then fixed by hand in AutoCAD.** No tool
   change, but repeated manual work on every drawing, and still inconsistent.
3. **One fixed grid of equal narrow columns; each field spans N grid columns
   using merged cells.** Every table has the same outer width; shared blocks sit
   in the same place in every table.

## Decision
Option 3. 24 equal grid columns, laid out as:

| Block | Grid columns |
|---|---|
| Tag | 2 |
| Description | 4 |
| Qty | 1 |
| Ratings | 12 (15 when the type has no dimensions) |
| Dimensions W/H/D | 3 |
| Notes | 2 |

12 divides by 2, 3, 4 and 6, so 4 to 7 rating fields fit evenly.
All schedules live on one sheet, so they share the same column widths.
The layout is defined once in `layout.yaml`; the builder works out the merges.

## Consequences
- Every table lines up, and AutoCAD Data Links of each table come in at the same width.
- Merged cells need care in openpyxl: write only the top-left cell of a merge.
- An equipment type with more than about 7 ratings won't fit neatly. That's a
  useful limit: it pushes detail into the specification instead of the drawing.
- To test: whether AutoCAD Data Link includes hidden spare rows.
