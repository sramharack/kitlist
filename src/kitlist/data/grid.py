"""The grid engine: turns layout.yaml into exact column positions and header cells.

Nothing here touches Excel. This module only answers "which grid columns does
each field occupy, and which header cells are merged?" Keeping that separate
from the workbook writer means the layout logic can be tested quickly and
reused by any output (Excel today, maybe DXF later).

Coordinates are 0-based: grid column 0 is the leftmost, header row 0 is the
title row. The writer converts to Excel's 1-based rows and columns.
"""

from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path

import yaml

BLOCK_ORDER = ("tag", "description", "qty", "ratings", "dimensions", "notes")
HEADER_ROWS = 4  # title, group label, field label, unit


class LayoutError(ValueError):
    """layout.yaml is invalid. The message says which type and what is wrong."""


@dataclass(frozen=True)
class Field:
    """One data column of a schedule, spanning one or more grid columns."""

    key: str
    label: str
    unit: str
    start: int  # first grid column
    span: int  # number of grid columns

    @property
    def end(self) -> int:
        """Last grid column (inclusive)."""
        return self.start + self.span - 1


@dataclass(frozen=True)
class HeaderCell:
    """One (possibly merged) header cell."""

    text: str
    row: int
    col: int
    row_span: int = 1
    col_span: int = 1


@dataclass(frozen=True)
class TableSpec:
    """Everything needed to draw one schedule."""

    key: str
    title: str
    fields: tuple[Field, ...]
    header: tuple[HeaderCell, ...]


@dataclass(frozen=True)
class Layout:
    columns: int
    column_width: float
    font: str
    font_size: float
    blank_rows: int
    blocks: dict
    types: dict

    def table(self, key: str) -> TableSpec:
        return table_spec(self, key)

    def tables(self) -> list[TableSpec]:
        return [table_spec(self, k) for k in self.types]


def load_layout(path: Path | None = None) -> Layout:
    """Read layout.yaml (the packaged one by default) and validate every type."""
    if path is None:
        text = files("kitlist").joinpath("data/layout.yaml").read_text(encoding="utf-8")
    else:
        text = Path(path).read_text(encoding="utf-8")
    raw = yaml.safe_load(text)
    grid = raw["grid"]
    layout = Layout(
        columns=int(grid["columns"]),
        column_width=float(grid["column_width"]),
        font=grid["font"],
        font_size=float(grid["font_size"]),
        blank_rows=int(grid.get("blank_rows", 3)),
        blocks=raw["blocks"],
        types=raw["types"],
    )
    layout.tables()  # build every table once so bad layouts fail at load time
    return layout


def _block_spans(layout: Layout, has_dims: bool) -> dict[str, int]:
    """Spans of the fixed blocks for a table, giving the dimension columns to
    ratings when the type has no dimensions."""
    spans = {name: int(layout.blocks[name]["span"]) for name in BLOCK_ORDER}
    if not has_dims:
        spans["ratings"] += spans["dimensions"]
        spans["dimensions"] = 0
    return spans


def table_spec(layout: Layout, key: str) -> TableSpec:
    """Work out every field position and header cell for one equipment type."""
    if key not in layout.types:
        raise LayoutError(f"unknown equipment type '{key}'")
    t = layout.types[key]
    has_dims = bool(t.get("dimensions", True))
    spans = _block_spans(layout, has_dims)

    if sum(spans.values()) != layout.columns:
        raise LayoutError(
            f"blocks add up to {sum(spans.values())} columns, grid has {layout.columns}"
        )

    ratings = t.get("ratings") or []
    if not ratings:
        raise LayoutError(f"'{key}' has no ratings")
    keys = [r["key"] for r in ratings]
    if len(set(keys)) != len(keys):
        raise LayoutError(f"'{key}' has duplicate rating keys: {keys}")
    for r in ratings:
        if not isinstance(r.get("span"), int) or r["span"] < 1:
            raise LayoutError(f"'{key}.{r['key']}' needs a whole-number span of at least 1")
    used = sum(r["span"] for r in ratings)
    if used != spans["ratings"]:
        raise LayoutError(
            f"'{key}' ratings span {used} columns but the ratings block is "
            f"{spans['ratings']} wide (12, or 15 without dimensions)"
        )

    fields: list[Field] = []
    header: list[HeaderCell] = [HeaderCell(t["title"], row=0, col=0, col_span=layout.columns)]
    col = 0
    for name in BLOCK_ORDER:
        block, width = layout.blocks[name], spans[name]
        if width == 0:
            continue
        if name == "ratings":
            header.append(HeaderCell(block["label"], row=1, col=col, col_span=width))
            for r in ratings:
                f = Field(r["key"], r["label"], r.get("unit", ""), col, r["span"])
                fields.append(f)
                header.append(HeaderCell(f.label, 2, f.start, col_span=f.span))
                header.append(HeaderCell(_unit(f.unit), 3, f.start, col_span=f.span))
                col += f.span
        elif name == "dimensions":
            header.append(HeaderCell(block["label"], row=1, col=col, col_span=width))
            for i, axis in enumerate(("width", "height", "depth")[:width]):
                f = Field(f"dim_{axis}", axis.upper(), block.get("unit", ""), col + i, 1)
                fields.append(f)
                header.append(HeaderCell(f.label, 2, f.start))
                header.append(HeaderCell(_unit(f.unit), 3, f.start))
            col += width
        else:
            f = Field(name, block["label"], "", col, width)
            fields.append(f)
            header.append(HeaderCell(f.label, 1, col, row_span=3, col_span=width))
            col += width

    return TableSpec(key, t["title"], tuple(fields), tuple(header))


def _unit(unit: str) -> str:
    return f"[{unit}]" if unit else ""
