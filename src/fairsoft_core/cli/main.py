import argparse

from fairsoft_core import __version__
from fairsoft_core.cli.commands.evaluate import run_evaluate_command
from fairsoft_core.cli.commands.indicator import run_indicator_command


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fairsoft",
        description="FAIRsoft CLI for research software metadata evaluation.",
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"fairsoft {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    evaluate_parser = subparsers.add_parser(
        "evaluate",
        help="Run full FAIRsoft evaluation on a metadata JSON file.",
    )
    evaluate_parser.add_argument(
        "input",
        help="Path to input metadata JSON file.",
    )
    evaluate_parser.add_argument(
        "--input-format",
        default="native",
        choices=["native", "codemeta"],
        help="Format of the input metadata file.",
    )
    evaluate_parser.add_argument(
        "-o",
        "--output",
        help="Optional output file path. Defaults to stdout.",
    )
    evaluate_parser.add_argument(
        "--select",
        default="full",
        choices=["full", "result", "logs", "feedback"],
        help="Which part of the evaluation output to return.",
    )
    evaluate_parser.add_argument(
        "--format",
        default="json",
        choices=["json", "json-compact"],
        help="Serialization format for the selected output.",
    )
    evaluate_parser.set_defaults(func=run_evaluate_command)

    indicator_parser = subparsers.add_parser(
        "indicator",
        help="Run a single indicator on a metadata JSON file.",
    )
    indicator_parser.add_argument(
        "indicator",
        nargs="?",
        help="Indicator identifier or name, for example F3_1 or searchability_in_registries.",
    )
    indicator_parser.add_argument(
        "input",
        nargs="?",
        help="Path to input metadata JSON file.",
    )
    indicator_parser.add_argument(
        "--list",
        action="store_true",
        help="List available indicators and exit.",
    )
    indicator_parser.add_argument(
        "--describe",
        metavar="INDICATOR",
        help="Show detailed information for one indicator and exit.",
    )
    indicator_parser.add_argument(
        "--input-format",
        default="native",
        choices=["native", "codemeta"],
        help="Format of the input metadata file.",
    )
    indicator_parser.add_argument(
        "-o",
        "--output",
        help="Optional output file path. Defaults to stdout.",
    )
    indicator_parser.add_argument(
        "--select",
        default="full",
        choices=["full", "result", "logs", "feedback"],
        help="Which part of the indicator output to return.",
    )
    indicator_parser.add_argument(
        "--format",
        default="json",
        choices=["json", "json-compact"],
        help="Serialization format for the selected output.",
    )
    indicator_parser.set_defaults(func=run_indicator_command)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
