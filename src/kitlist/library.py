"""Equipment libraries: standard sizes read from the CSV files in data/library/.

Every row cites a source listed in docs/design-basis.md (NFR-05).
"""

import csv
from dataclasses import dataclass
from importlib.resources import files

FAMILIES = ("ieee-dry", "ieee-pad", "iec")  # transformer rating families (D7)


@dataclass(frozen=True)
class TransformerRating:
    """One row of transformer_kva.csv."""

    family: str
    phase: int
    kva: float
    source: str


def transformer_ratings() -> list[TransformerRating]:
    """Every standard transformer rating in the library."""
    path = files("kitlist").joinpath("data/library/transformer_kva.csv")
    # "utf-8-sig" also accepts the invisible marker Excel adds when it saves a CSV.
    text = path.read_text(encoding="utf-8-sig")
    return [
        TransformerRating(row["family"], int(row["phase"]), float(row["kva"]), row["source"])
        for row in csv.DictReader(text.splitlines())
    ]


def transformer_sizes(family: str, phase: int) -> list[float]:
    """Standard kVA sizes for one family and phase count, smallest first."""
    if family not in FAMILIES:
        raise ValueError(f"unknown transformer family '{family}'; expected one of {FAMILIES}")
    return sorted(r.kva for r in transformer_ratings() if r.family == family and r.phase == phase)
