<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/assets/logo-dark.svg">
    <img alt="kitlist" src="docs/assets/logo-light.svg" width="340">
  </picture>
</p>

<p align="center"><b>Aligned, macro-free equipment schedules for MEP drawings, with built-in sizing and checks.</b></p>

<p align="center">
  <a href="https://github.com/OWNER/kitlist/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/OWNER/kitlist/actions/workflows/ci.yml/badge.svg"></a>
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-1F3A5F"></a>
</p>

Fill in a few inputs per item (load, location, system voltage) and get drawing-ready
schedules for generators, transfer switches, transformers, disconnects, surge protection
and more. Every table lines up on the drawing, and the workbook is plain Excel:
no macros, no add-ins, nothing to install.

> **Status: early development.** The design is settled and the first sizing rule is in
> place, but there is no workbook to download yet. v0.1.0 is planned to cover the five
> equipment types marked below. Watch or star the repo to follow along.

## The problem

Most firms build equipment schedules by hand, one Excel table per equipment type. Each
table ends up with its own column widths, so stacked on a drawing they don't line up,
headers get cut off, and pasting into AutoCAD needs fiddling every time. The sizing behind
each row is done in someone's head or a separate calc, and simple mistakes slip through
(a generator whose prime rating is higher than its standby rating, say).

## What kitlist does

- **One grid for every schedule.** All tables sit on a shared 24-column grid, so they have
  the same width, and Tag, Description, Qty, Dimensions and Notes are in the same place in
  every table. Fields span grid columns, so a schedule with four ratings and one with seven
  still line up. ([why](docs/decisions/0001-shared-24-column-grid.md))
- **Sizes equipment from standard ranges.** Enter the load and spare capacity; it picks the
  next standard size (kVA, frame, switch rating) from editable library tables.
- **Checks as you go.** Each row is checked against simple engineering rules, and problems
  are shown next to the row rather than discovered at review.
- **Plain Excel at runtime.** Selection and checks are ordinary Excel formulas using
  Excel-2007-era functions only, so the workbook works in desktop Excel, Excel online
  and LibreOffice, and can be emailed like any other file.
- **Brandable.** Build profiles add your firm's name, logo and default settings without
  touching the code.
- **Doesn't over-specify.** Each schedule shows what a drawing needs, typically five to seven
  ratings plus dimensions. Detailed requirements belong in the specification.

## Equipment covered

| Equipment | Status |
|---|---|
| Power / isolation transformers, incl. buck-boost | planned for v0.1 |
| Diesel generators | planned for v0.1 |
| Automatic transfer switches | planned for v0.1 |
| Disconnect switches | planned for v0.1 |
| Surge protection devices | planned for v0.1 |
| UPS | later |
| LV switchgear | later |
| Meter module stacks | later |
| Lightning protection components | later |

## Using the workbook

*Available from v0.1.0.*

1. Download `kitlist.xlsx` from [Releases](../../releases).
2. Set the project defaults (system voltages, frequency, enclosure for indoor/outdoor) on
   the **Project** sheet.
3. Add your equipment on each input sheet. Yellow cells are inputs; everything else is
   calculated.
4. Read the **Schedules** sheet. It prints as-is, or link each schedule into AutoCAD with
   `DATALINK` so the drawing updates when the workbook changes.

## How it works

Python *builds* the workbook; Excel *runs* it.

```
layout.yaml + library CSVs + profile ──▶  build  ──▶  kitlist.xlsx
                                              │
                         tests ◀──────────────┘  (Python rule == Excel formula?)
```

Every rule is written twice: once in Python as the reference, where it is easy to test and
review, and once as the Excel formula the builder writes into the workbook. Automated tests
recalculate the workbook and check that both give the same answer.
([why](docs/decisions/0002-python-reference-excel-runtime.md))

## Roadmap

| Milestone | Scope |
|---|---|
| M0 | Repo, tests and CI ✔ |
| M1 | Requirements and `layout.yaml` |
| M2 | Grid engine: field spans to merged cells |
| M3 | Selectors and equipment libraries for the five v0.1 types |
| M4 | Workbook builder and build profiles |
| M5 | Release automation and visual regression tests |
| M6 | AutoCAD Data Link trial and pilot use → **v0.1.0** |

## Development

You need [uv](https://docs.astral.sh/uv/).

```bash
uv sync                                       # set up the environment
uv run pytest                                 # run the tests
uv run ruff check . && uv run ruff format .   # lint and format
```

New to the codebase? Start with [docs/learning/m0-walkthrough.md](docs/learning/m0-walkthrough.md).
Design decisions are recorded in [docs/decisions](docs/decisions).

```
src/kitlist/      the package: sizing rules, grid engine, workbook builder
tests/              pytest tests, one file per module
docs/decisions/     architecture decision records
docs/learning/      walkthroughs for each milestone
```

## Contributing

Issues are welcome, especially:
- equipment types you schedule often;
- fields your schedules always include;
- cases where a selection looks wrong.

Pull requests should include tests. For anything beyond a small fix, open an issue first
so we can agree the approach.

## License

[MIT](LICENSE).

## Disclaimer

kitlist helps select and schedule equipment. It does not replace engineering judgement.
Verify every selection against the codes adopted for your project, the manufacturer's data
and the project specification. Standards are cited by clause; their text is not reproduced.
