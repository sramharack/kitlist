"""Command line entry point: `uv run kitlist preview`."""

import argparse
from pathlib import Path

from kitlist.grid import load_layout
from kitlist.writer import write_preview


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="kitlist", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("preview", help="write every schedule's header grid to an .xlsx file")
    p.add_argument("-o", "--out", type=Path, default=Path("out/kitlist-preview.xlsx"))
    p.add_argument("--layout", type=Path, help="layout.yaml to use (default: the packaged one)")

    args = parser.parse_args(argv)
    if args.command == "preview":
        args.out.parent.mkdir(parents=True, exist_ok=True)
        path = write_preview(load_layout(args.layout), args.out)
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
