"""Tests for the Excel preview writer (REQ-01, REQ-04, REQ-05, REQ-10)."""

import pytest
from openpyxl import load_workbook

from kitlist.grid import HEADER_ROWS, load_layout
from kitlist.writer import range_name, sheet_name, write_preview

LAYOUT = load_layout()
TABLES = LAYOUT.tables()
IDS = [t.key for t in TABLES]


@pytest.fixture(scope="module")
def wb(tmp_path_factory):
    path = write_preview(LAYOUT, tmp_path_factory.mktemp("out") / "preview.xlsx")
    return load_workbook(path)


def test_each_equipment_type_has_its_own_sheet(wb):  # REQ-10, ADR 0004
    assert wb.sheetnames == [sheet_name(t) for t in TABLES]


def test_every_sheet_uses_the_same_column_widths(wb):  # REQ-01
    widths = {
        ws.column_dimensions[c].width for ws in wb.worksheets for c in "ABCDEFGHIJKLMNOPQRSTUVWX"
    }
    assert widths == {LAYOUT.column_width}


@pytest.mark.parametrize("spec", TABLES, ids=IDS)
def test_each_table_is_a_named_range_on_its_own_sheet(wb, spec):  # REQ-04
    ref = wb.defined_names[range_name(spec)].attr_text  # e.g. 'Generators'!$A$1:$X$7
    sheet, cells = ref.rsplit("!", 1)
    first, last = cells.replace("$", "").split(":")
    assert sheet.strip("'") == sheet_name(spec)
    assert (first, last) == ("A1", f"X{HEADER_ROWS + LAYOUT.start_rows}")
    assert wb[sheet_name(spec)]["A1"].value == spec.title


@pytest.mark.parametrize("spec", TABLES, ids=IDS)
def test_every_sheet_prints_landscape_fit_to_width(wb, spec):  # REQ-05
    ws = wb[sheet_name(spec)]
    assert ws.page_setup.orientation == "landscape"
    assert ws.page_setup.fitToWidth == 1 and ws.page_setup.fitToHeight == 0


def test_sheet_names_are_valid_excel_names():
    for spec in TABLES:
        name = sheet_name(spec)
        assert 0 < len(name) <= 31 and not set(name) & set("[]:*?/\\")
