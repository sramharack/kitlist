"""Tests for the equipment libraries (NFR-05, REQ-11)."""

from pathlib import Path

import pytest

from kitlist.library import FAMILIES, transformer_ratings, transformer_sizes

DESIGN_BASIS = Path(__file__).parents[1] / "docs" / "design-basis.md"
RATINGS = transformer_ratings()


def reference_ids() -> set[str]:
    """The IDs in the first column of the References table in docs/design-basis.md."""
    text = DESIGN_BASIS.read_text(encoding="utf-8")
    references = text.split("## References")[1].split("\n## ")[0]
    ids = set()
    for line in references.splitlines():
        if not line.startswith("|"):
            continue
        first_cell = line.split("|")[1].strip()
        if first_cell != "ID" and not first_cell.startswith("---"):
            ids.add(first_cell)
    return ids


# ---- traceability (NFR-05) ----


def test_reference_table_can_be_read():
    # Checks the helper above: if this fails, the other tests can't be trusted.
    assert {"DOE-431.196a", "DOE-431.196b", "IEC-60076-1"} <= reference_ids()


def test_every_rating_cites_a_source_listed_in_the_design_basis():
    missing = {r.source for r in RATINGS} - reference_ids()
    assert not missing, f"not listed in docs/design-basis.md: {sorted(missing)}"


# ---- families (REQ-11, D7) ----


def test_every_rating_belongs_to_a_known_family():
    unknown = {r.family for r in RATINGS} - set(FAMILIES)
    assert not unknown, f"unknown families: {sorted(unknown)}"


def test_families_are_never_mixed():
    # 25 kVA three-phase is an IEC rating, not a North American one
    assert 25 in transformer_sizes("iec", phase=3)
    assert 25 not in transformer_sizes("ieee-dry", phase=3)


def test_unknown_family_is_an_error():
    with pytest.raises(ValueError, match="unknown transformer family"):
        transformer_sizes("ansi", phase=3)


# ---- library contents ----


def test_no_rating_is_listed_twice():
    keys = [(r.family, r.phase, r.kva) for r in RATINGS]
    assert len(keys) == len(set(keys))


def test_sizes_come_back_smallest_first():
    sizes = transformer_sizes("ieee-dry", phase=3)
    assert sizes == sorted(sizes)


def test_single_phase_padmounts_stay_within_c57_12_38_scope():
    assert max(transformer_sizes("ieee-pad", phase=1)) <= 250