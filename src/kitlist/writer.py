"""Write schedules to Excel from the grid engine's TableSpecs.

Each equipment type gets its own sheet (ADR 0004). Every sheet uses the same
column widths, so the tables still line up when pasted into a drawing.

For now this draws headers and starter rows only: a preview to check alignment
and to trial pasting into AutoCAD. Inputs, formulas and checks come in M4.
"""

from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, Side
from openpyxl.utils import get_column_letter
from openpyxl.workbook.defined_name import DefinedName

from kitlist.grid import HEADER_ROWS, Layout, TableSpec

THIN = Side(style="thin", color="000000")
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
CENTRE = Alignment(horizontal="center", vertical="center", wrap_text=True)
LEFT = Alignment(horizontal="left", vertical="center", wrap_text=True)
# Points per header row: title, group (two lines, for "PROVISIONAL DIMENSIONS"),
# field label (two lines), unit.
ROW_HEIGHTS = (14, 22, 24, 11)
DATA_ROW_HEIGHT = 12.75
LEFT_ALIGNED = {"description", "notes"}
_BAD_SHEET_CHARS = str.maketrans({c: " " for c in "[]:*?/\\"})


def range_name(spec: TableSpec) -> str:
    """Excel name for a table's range, e.g. SCH_TRANSFORMER. Select it in the Name Box
    to copy the whole table; a future AutoCAD Data Link can target the same name."""
    return f"SCH_{spec.key.upper()}"


def sheet_name(spec: TableSpec) -> str:
    """Sheet tab name from the table title, e.g. 'Automatic Transfer Switches'.
    Excel allows at most 31 characters and none of [ ] : * ? / \\ ."""
    return spec.title.title().translate(_BAD_SHEET_CHARS).strip()[:31]


def write_preview(layout: Layout, path: Path) -> Path:
    """Write every schedule, one sheet per equipment type, to an .xlsx file."""
    wb = Workbook()
    wb.remove(wb.active)  # start with no sheets; we add one per type

    for spec in layout.tables():
        ws = wb.create_sheet(sheet_name(spec))
        ws.sheet_view.showGridLines = False
        for c in range(1, layout.columns + 1):
            ws.column_dimensions[get_column_letter(c)].width = layout.column_width

        last_row = _write_table(ws, layout, spec, top=1)
        last_col = get_column_letter(layout.columns)
        wb.defined_names[range_name(spec)] = DefinedName(
            range_name(spec), attr_text=f"'{ws.title}'!$A$1:${last_col}${last_row}"
        )

        ws.print_area = f"A1:{last_col}{last_row}"
        ws.page_setup.orientation = "landscape"
        ws.page_setup.fitToWidth, ws.page_setup.fitToHeight = 1, 0
        ws.sheet_properties.pageSetUpPr.fitToPage = True

    path = Path(path)
    wb.save(path)
    return path


def _write_table(ws, layout: Layout, spec: TableSpec, top: int) -> int:
    """Draw one table with its top-left at row `top`. Returns its last row."""
    n_rows = HEADER_ROWS + layout.start_rows
    font = Font(name=layout.font, size=layout.font_size)
    bold = Font(name=layout.font, size=layout.font_size, bold=True)

    # Box every cell first, so merged ranges get complete borders
    for r in range(top, top + n_rows):
        for c in range(1, layout.columns + 1):
            cell = ws.cell(r, c)
            cell.border, cell.font, cell.alignment = BOX, font, CENTRE

    for i, h in enumerate(ROW_HEIGHTS):
        ws.row_dimensions[top + i].height = h
    for r in range(top + HEADER_ROWS, top + n_rows):
        ws.row_dimensions[r].height = DATA_ROW_HEIGHT

    for h in spec.header:
        r, c = top + h.row, h.col + 1
        cell = ws.cell(r, c, h.text)
        cell.font = (
            Font(name=layout.font, size=layout.font_size + 1, bold=True) if h.row == 0 else bold
        )
        if h.row_span > 1 or h.col_span > 1:
            ws.merge_cells(
                start_row=r,
                start_column=c,
                end_row=r + h.row_span - 1,
                end_column=c + h.col_span - 1,
            )

    for r in range(top + HEADER_ROWS, top + n_rows):
        for f in spec.fields:
            if f.key in LEFT_ALIGNED:
                ws.cell(r, f.start + 1).alignment = LEFT
            if f.span > 1:
                ws.merge_cells(
                    start_row=r, start_column=f.start + 1, end_row=r, end_column=f.end + 1
                )

    return top + n_rows - 1
