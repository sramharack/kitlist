# Design basis

Every value in kitlist's equipment libraries traces to a cited source, so any
standard size can be checked against the document it came from.

## How sources are recorded

- Each library CSV in `src/kitlist/data/library/` has a `source` column holding a
  reference ID from the table below.
- A test fails if a library uses an ID that isn't listed here, so no value can be
  added without a source.
- Paywalled standards are cited by edition and clause. Their text is not reproduced.

## References

| ID | Document | Used for | Verified | Notes |
|---|---|---|---|---|
| DOE-431.196a | US 10 CFR 431.196(a)(2), low-voltage dry-type distribution transformers, table for units made 2016–2029 | `ieee-dry` kVA ratings | Against the regulation text, 2026-11-08 | Applies legally to 60 Hz units sold in the US; cited as a public record of the North American rating series. Free at ecfr.gov. |
| DOE-431.196b | US 10 CFR 431.196(b)(2), liquid-immersed distribution transformers, Table 5 | `ieee-pad` kVA ratings, limited to the scope of IEEE-C57.12.38 (single-phase, ≤ 250 kVA) and IEEE-C57.12.34 (three-phase) | Against the regulation text, 2026-11-08 | Same note as above. |
| IEC-60076-1 | IEC 60076-1:2011, Power transformers – Part 1: General, clause 5.1.2 (preferred values of rated power, R10 series of ISO 3) | `iec` kVA ratings | **No** | Values are the R10 preferred numbers. Paywalled; verify against a copy before relying on this family. |
| IEEE-C57.12.38 | IEEE C57.12.38-2025, pad-mounted, self-cooled, single-phase distribution transformers, 250 kVA and smaller | Scope of `ieee-pad` single-phase | Scope only, from the published abstract | Scope is 60 Hz; on 50 Hz projects, specify "in general accordance with, except 50 Hz". Paywalled. |
| IEEE-C57.12.34 | IEEE C57.12.34-2022, pad-mounted, compartmental-type, self-cooled, three-phase distribution transformers, 10 MVA and smaller | Scope of `ieee-pad` three-phase | Scope only, from the published abstract | Same note. Paywalled. |

## Transformers

Library: `transformer_kva.csv`, one row per standard rating, tagged by family (D7):

- `ieee-dry`: low-voltage dry-type, North American series (DOE-431.196a).
- `ieee-pad`: liquid-filled padmount, North American series (DOE-431.196b), within the
  scope of IEEE C57.12.38 (single-phase) and C57.12.34 (three-phase).
- `iec`: IEC series (IEC-60076-1). Not yet verified against the standard.

These are *standard* ratings. Sizes local suppliers rarely stock (for example
10 kVA single-phase padmounts or 31.5 kVA IEC units) are still listed; trimming the
list to what is buyable is a separate, project-level decision.