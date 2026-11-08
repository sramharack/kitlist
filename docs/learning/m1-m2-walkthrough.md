# M1–M2 walkthrough: requirements, layout and the grid engine

What exists now:

```
docs/requirements.md          numbered requirements and engineering decisions
src/kitlist/data/layout.yaml  the grid and every schedule's fields
src/kitlist/grid.py           reads + validates the layout, works out every cell
src/kitlist/writer.py         draws each schedule on its own sheet
src/kitlist/cli.py            `uv run kitlist preview`
tests/                        test_grid.py, test_writer.py, test_sizing.py
```

## 1. See it

```bash
uv run kitlist preview        # writes out/kitlist-preview.xlsx
```

Open it in Excel: one sheet per equipment type, all the same width. Change something in
`layout.yaml` (e.g. swap the spans of two transformer ratings), run preview again and look.

Now make a mistake on purpose: set one transformer rating span to 3 and run the preview.
Read the error. Then `uv run pytest` and see which tests fail. Undo it.

## 2. Read the code

Read `grid.py` top to bottom (about 150 lines). Things to notice:

- **Separation of concerns.** `grid.py` never mentions Excel. It produces plain data
  (`TableSpec`, `Field`, `HeaderCell`); `writer.py` only draws. The layout logic is tested
  in milliseconds without opening a workbook, and a DXF writer could reuse it later.
- **`@dataclass(frozen=True)`**: a small class that just holds data. `frozen` means it
  can't be changed after it's made, so a `Field` can't be moved by accident.
- **`@property`**: `field.end` looks like a stored value but is calculated, so it can
  never disagree with `start` and `span`.
- **Fail early, fail clearly.** `load_layout` builds every table once on load, so a bad
  layout fails before anything is written, with a message naming the type.
- **`importlib.resources.files`** finds `layout.yaml` inside the installed package, so it
  works wherever the package is installed (including from `mep-tools`).

Then read the tests:

- **Invariant tests.** `test_header_cells_cover_every_grid_position_exactly_once` checks a
  property that must hold for *every* table, including types that don't exist yet.
- **Breaking a copy of real data.** The `raw` fixture loads the real layout, a test breaks
  one thing, and checks the right error appears.
- **Decision tests** (`test_d1_...`) pin your engineering decisions. Changing a decision
  means changing its test on purpose, which shows up in review.

## 3. Your tasks

1. **Paste trial.** Open `kitlist-preview.xlsx`. On the Generators sheet, type
   `SCH_GENERATOR` in the Name Box, Enter, copy, then in AutoCAD use
   **Paste Special > AutoCAD Entities**. Do the same for `SCH_SPD` below it. Check:
   - both tables paste at the same width;
   - merges, borders and the two-line PROVISIONAL DIMENSIONS header survive;
   - adding a row (copy a row, *Insert Copied Cells* on the last row) grows the named range.
   Record the results in a GitHub issue titled "AutoCAD paste trial", with screenshots.
2. **Generator checks** (from the M0 walkthrough), using decision D5.
