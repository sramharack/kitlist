"""Tests for kitlist.sizing.

Each test name says the engineering rule it checks, so a failing test
reads like a failed design check.
"""

import pytest

from kitlist.sizing import next_standard_size

# Common three-phase dry-type transformer sizes (kVA). Test data only;
# the real library will live in a CSV file (milestone M3).
XFMR_KVA = [15, 30, 45, 75, 112.5, 150, 225, 300, 500]


@pytest.mark.parametrize(
    ("required", "spare", "expected"),
    [
        (75, 0.25, 112.5),  # 93.75 kVA needed -> next size up
        (75, 0.0, 75),  # an exact match is enough
        (10, 0.0, 15),  # small load -> smallest unit
        (240, 0.25, 300),  # 300 kVA needed -> exact match after spare
    ],
)
def test_picks_smallest_size_that_covers_load_plus_spare(required, spare, expected):
    assert next_standard_size(required, XFMR_KVA, spare) == expected


def test_order_of_sizes_does_not_matter():
    assert next_standard_size(50, reversed(XFMR_KVA), spare=0.0) == 75


def test_float_noise_does_not_bump_to_next_size():
    # 0.1 + 0.2 is 0.30000000000000004 in floating point
    assert next_standard_size(0.1 + 0.2, [0.3, 0.5], spare=0.0) == 0.3


def test_load_above_largest_size_is_an_error():
    with pytest.raises(ValueError, match="exceeds the largest"):
        next_standard_size(450, XFMR_KVA, spare=0.25)  # 562.5 > 500


@pytest.mark.parametrize(
    ("required", "sizes", "spare"),
    [
        (-1, XFMR_KVA, 0.0),  # negative load
        (10, XFMR_KVA, -0.1),  # negative spare
        (10, [], 0.0),  # nothing to choose from
    ],
)
def test_bad_inputs_are_rejected(required, sizes, spare):
    with pytest.raises(ValueError):
        next_standard_size(required, sizes, spare)
