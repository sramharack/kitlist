"""Tests for the grid engine (REQ-01 to REQ-03 in docs/requirements.md)."""

from collections import Counter
from importlib.resources import files

import pytest
import yaml

from kitlist.grid import HEADER_ROWS, LayoutError, load_layout

LAYOUT = load_layout()
TABLES = LAYOUT.tables()
IDS = [t.key for t in TABLES]


def first(spec, key):
    return next(f for f in spec.fields if f.key == key)


@pytest.mark.parametrize("spec", TABLES, ids=IDS)
def test_every_table_fills_the_grid_with_no_gaps_or_overlaps(spec):  # REQ-01
    col = 0
    for f in spec.fields:
        assert f.start == col, f"{spec.key}.{f.key} starts at {f.start}, expected {col}"
        col = f.end + 1
    assert col == LAYOUT.columns


@pytest.mark.parametrize("block", ["tag", "description", "qty", "notes"])
def test_shared_blocks_sit_in_the_same_columns_in_every_table(block):  # REQ-01
    positions = {(first(t, block).start, first(t, block).span) for t in TABLES}
    assert len(positions) == 1, f"'{block}' moves between tables: {positions}"


def test_dimension_columns_line_up_wherever_they_appear():  # REQ-01
    starts = {first(t, "dim_width").start for t in TABLES if t.key != "spd"}
    assert len(starts) == 1


def test_types_without_dimensions_give_those_columns_to_ratings():
    spd = LAYOUT.table("spd")
    assert not any(f.key.startswith("dim_") for f in spd.fields)
    assert first(spd, "notes").start == first(LAYOUT.table("generator"), "notes").start


@pytest.mark.parametrize("spec", TABLES, ids=IDS)
def test_header_cells_cover_every_grid_position_exactly_once(spec):  # REQ-03
    covered = Counter(
        (h.row + dr, h.col + dc)
        for h in spec.header
        for dr in range(h.row_span)
        for dc in range(h.col_span)
    )
    expected = {(r, c) for r in range(HEADER_ROWS) for c in range(LAYOUT.columns)}
    assert set(covered) == expected, "header has holes or spills outside the grid"
    assert max(covered.values()) == 1, "some header cells overlap"


def test_units_are_shown_in_brackets():  # REQ-03
    unit_cells = [h.text for h in LAYOUT.table("transformer").header if h.row == 3 and h.text]
    assert "[kVA]" in unit_cells
    assert all(u.startswith("[") and u.endswith("]") for u in unit_cells)


# ---- invalid layouts are rejected with a useful message (REQ-02) ----


@pytest.fixture
def raw():
    """The packaged layout as a plain dict, ready to be broken on purpose."""
    return yaml.safe_load(files("kitlist").joinpath("data/layout.yaml").read_text("utf-8"))


def load(raw, tmp_path):
    path = tmp_path / "layout.yaml"
    path.write_text(yaml.safe_dump(raw, allow_unicode=True), encoding="utf-8")
    return load_layout(path)


def test_ratings_that_do_not_fill_their_block_are_rejected(raw, tmp_path):
    raw["types"]["transformer"]["ratings"][0]["span"] = 3  # now 13 wide
    with pytest.raises(LayoutError, match="'transformer' ratings span 13"):
        load(raw, tmp_path)


def test_duplicate_rating_keys_are_rejected(raw, tmp_path):
    ratings = raw["types"]["ats"]["ratings"]
    ratings[1]["key"] = ratings[0]["key"]
    with pytest.raises(LayoutError, match="duplicate"):
        load(raw, tmp_path)


def test_zero_or_fractional_spans_are_rejected(raw, tmp_path):
    raw["types"]["spd"]["ratings"][0]["span"] = 0
    with pytest.raises(LayoutError, match="spd.type"):
        load(raw, tmp_path)


def test_blocks_that_do_not_add_up_to_the_grid_are_rejected(raw, tmp_path):
    raw["blocks"]["notes"]["span"] = 3
    with pytest.raises(LayoutError, match="blocks add up to 25"):
        load(raw, tmp_path)


def test_unknown_equipment_type_is_rejected():
    with pytest.raises(LayoutError, match="unknown equipment type 'ups'"):
        LAYOUT.table("ups")
