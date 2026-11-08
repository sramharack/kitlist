# 0003: The layout lives in a data file, not in code

- **Status:** accepted
- **Date:** 2026-11-07

## Context
Schedule fields change more often than the code: a new rating column, a different span,
a new equipment type. Each change should be easy to review, and a mistake should be
caught before it reaches a drawing.

## Options considered
1. **Fields defined in Python.** Flexible, but every layout tweak is a code change, and
   the layout is spread across the code.
2. **Fields defined in a spreadsheet.** Familiar to engineers, but awkward to review in
   a pull request (binary file, no readable diff).
3. **Fields defined in a YAML file, validated by the grid engine on load.**

## Decision
Option 3. `src/kitlist/data/layout.yaml` defines the grid, the fixed blocks and every
equipment type. `kitlist.grid.load_layout` validates it and refuses to load a layout that
breaks the grid, naming the type and the problem.

## Consequences
- Adding an equipment type is a YAML edit plus tests, with a readable diff.
- The rules for a valid layout live in one function and are tested by deliberately
  breaking a copy of the real layout.
- YAML has pitfalls (indentation, `no` read as false). Keys and labels should stay
  simple text; validation catches most mistakes.
