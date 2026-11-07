"""Pick standard equipment sizes.

Most selectors in this tool reduce to one question: given a required rating,
what is the smallest standard size that covers it? This module answers that.

This Python version is the *reference implementation* (see ADR 0002). The
workbook does the same job with an Excel formula, and the tests check that
both give the same answer.
"""

from collections.abc import Iterable

# Floating-point arithmetic is not exact: 0.1 + 0.2 gives 0.30000000000000004.
# Without a tolerance, a requirement that is "really" 0.3 would skip past a
# 0.3 size to the next one up. A requirement within this relative tolerance
# of a standard size is treated as equal to it.
REL_TOL = 1e-9


def next_standard_size(required: float, sizes: Iterable[float], spare: float) -> float:
    """Return the smallest standard size that covers ``required * (1 + spare)``.

    Args:
        required: Load the equipment must carry, in the same unit as ``sizes``
            (kVA, A, ...). Must be zero or positive.
        sizes: Standard sizes available, in any order.
        spare: Spare capacity as a fraction (0.25 means 25 %). Must be zero or positive.

    Returns:
        The selected standard size.

    Raises:
        ValueError: If an input is negative, ``sizes`` is empty, or the load is
            bigger than the largest standard size.

    Example (pytest runs this too, as a "doctest"):

    >>> next_standard_size(75, [45, 75, 112.5, 150], spare=0.25)
    112.5
    """
    if required < 0:
        raise ValueError(f"required must be zero or positive, got {required}")
    if spare < 0:
        raise ValueError(f"spare must be zero or positive, got {spare}")

    ordered = sorted(sizes)
    if not ordered:
        raise ValueError("no standard sizes given")

    target = required * (1 + spare)
    for size in ordered:
        if size >= target * (1 - REL_TOL):
            return size

    raise ValueError(
        f"required {target:g} (incl. spare) exceeds the largest standard size {ordered[-1]:g}"
    )
