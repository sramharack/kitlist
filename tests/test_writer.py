"""Tests for the Excel preview writer (REQ-01, REQ-04, REQ-05)."""

import pytest
from openpyxl import load_workbook

from kitlist.grid import load_layout
from kitlist.writer import range_name, write_preview

LAYOUT = load_layout()


@pytest.fixture(scope="module")
def ws_and_wb(tmp_path_factory):
    path = write_preview(LAYOUT, tmp_path_factory.mktemp("out") / "preview.xlsx")
    wb = load_workbook(path)
    return wb["Schedules"], wb


def test_all_grid_columns_have_the_same_width(ws_and_wb):  # REQ-01
    ws, _ = ws_and_wb
    widths = {ws.column_dimensions[c].width for c in "ABCDEFGHIJKLMNOPQRSTUVWX"}
    assert widths == {LAYOUT.column_width}


@pytest.mark.parametrize("spec", LAYOUT.tables(), ids=lambda s: s.key)
def test_each_table_is_a_named_range_spanning_the_full_grid(ws_and_wb, spec):  # REQ-04
    ws, wb = ws_and_wb
    ref = wb.defined_names[range_name(spec)].attr_text  # e.g. Schedules!$A$1:$X$7
    first, last = ref.split("!")[1].replace("$", "").split(":")
    assert first.startswith("A") and last.startswith("X")
    assert ws[first].value == spec.title


def test_sheet_prints_landscape_fit_to_width(ws_and_wb):  # REQ-05
    ws, _ = ws_and_wb
    assert ws.page_setup.orientation == "landscape"
    assert ws.page_setup.fitToWidth == 1 and ws.page_setup.fitToHeight == 0
