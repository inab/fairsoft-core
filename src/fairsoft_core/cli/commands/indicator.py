import sys
from typing import Any, Callable

from fairsoft_core.cli.io import (
    load_json_file,
    render_output,
    select_output_payload,
    write_output,
)
from fairsoft_core.exceptions import InstanceCreationError
from fairsoft_core.indicators.f_indicators import compF3_1
from fairsoft_core.models.instance import Instance

IndicatorFunc = Callable[[Instance], tuple[bool, list[str]]]


AVAILABLE_INDICATORS: dict[str, dict[str, Any]] = {
    "F3_1": {
        "name": "searchability_in_registries",
        "description": "Searchability in registries.",
        "function": compF3_1,
    },
    # Future additions:
    # "F3_2": {
    #     "name": "searchability_in_search_engines",
    #     "description": "...",
    #     "function": compF3_2,
    # },
    # "F3_3": {
    #     "name": "searchability_in_software_catalogues",
    #     "description": "...",
    #     "function": compF3_3,
    # },
}


def _build_indicator_aliases() -> dict[str, str]:
    aliases: dict[str, str] = {}
    for indicator_id, spec in AVAILABLE_INDICATORS.items():
        aliases[indicator_id.lower()] = indicator_id
        aliases[spec["name"].lower()] = indicator_id
    return aliases


INDICATOR_ALIASES = _build_indicator_aliases()


def _list_available_indicators() -> str:
    lines = ["Available indicators:"]
    for indicator_id, spec in AVAILABLE_INDICATORS.items():
        lines.append(f"  - {indicator_id}: {spec['name']} — {spec['description']}")
    return "\n".join(lines)


def _resolve_indicator(indicator_value: str | None) -> str | None:
    if indicator_value is None:
        return None
    return INDICATOR_ALIASES.get(indicator_value.lower())


def _run_single_indicator(
    indicator_func: IndicatorFunc,
    tool_metadata: dict[str, Any],
) -> dict[str, Any]:
    try:
        instance = Instance(**tool_metadata)
    except Exception as e:
        raise InstanceCreationError(str(e)) from e

    passed, logs = indicator_func(instance)

    return {
        "result": passed,
        "logs": logs,
        "feedback": [],
    }


def run_indicator_command(args) -> int:
    try:
        if args.list:
            print(_list_available_indicators())
            return 0

        if not args.indicator:
            print(
                "Error: missing indicator. Use 'fairsoft indicator --list' to see available indicators.",
                file=sys.stderr,
            )
            return 2

        if not args.input:
            print(
                "Error: missing input file.",
                file=sys.stderr,
            )
            return 2

        resolved_indicator = _resolve_indicator(args.indicator)
        if not resolved_indicator:
            print(
                f"Unknown indicator '{args.indicator}'. Use 'fairsoft indicator --list' to see available indicators.",
                file=sys.stderr,
            )
            return 2

        tool_metadata = load_json_file(args.input)

        indicator_func = AVAILABLE_INDICATORS[resolved_indicator]["function"]
        result = _run_single_indicator(
            indicator_func=indicator_func,
            tool_metadata=tool_metadata,
        )

        payload = select_output_payload(result, args.select)
        rendered = render_output(payload, args.format)
        write_output(rendered, args.output)
        return 0

    except InstanceCreationError as e:
        print(f"Input error: {e}", file=sys.stderr)
        return 2

    except FileNotFoundError:
        print(f"File not found: {args.input}", file=sys.stderr)
        return 4

    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1
