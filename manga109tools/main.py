import argparse
from pathlib import Path
import pytest
import sys


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--root_dir", default=Path("./"), type=Path)
    subparsers = parser.add_subparsers(title="commands", dest="command", required=True)
    parser_val = subparsers.add_parser("validate")
    parser_val.add_argument("--target_annot", default="annotations")
    parser_val.add_argument(
        "--exception_path",
        default=Path.home() / ".manga109tools" / "exceptions.yaml",
        type=Path,
    )
    return parser.parse_args()


def main():
    args: argparse.Namespace = parse_args()
    test_root: Path = Path(__file__).parent / "tests"
    if args.command == "validate":
        pytest_args = [
            test_root.as_posix(),
            "--durations",
            "0",
            "--root_dir",
            args.root_dir.as_posix(),
            "--target_annot",
            args.target_annot,
            "--exception_path",
            args.exception_path.as_posix(),
        ]

        exit_code = pytest.main(pytest_args)
        sys.exit(exit_code)
    else:
        raise NotImplementedError


if __name__ == "__main__":
    main()
