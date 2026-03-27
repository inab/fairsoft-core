import sys

from fairsoft_core.cli.io import (
    load_json_file,
    render_output,
    select_output_payload,
    write_output,
)
from fairsoft_core.evaluation.all_indicators import run_fairsoft_evaluation
from fairsoft_core.exceptions import (
    FairScoreComputationError,
    IndicatorComputationError,
    InstanceCreationError,
)
from fairsoft_core.inputs import normalize_input


def run_evaluate_command(args) -> int:
    try:
        raw_data = load_json_file(args.input)
        tool_metadata = normalize_input(raw_data, args.input_format)
        result = run_fairsoft_evaluation(tool_metadata=tool_metadata)

        payload = select_output_payload(result, args.select)
        rendered = render_output(payload, args.format)
        write_output(rendered, args.output)
        return 0

    except InstanceCreationError as e:
        print(f"Input error: {e}", file=sys.stderr)
        return 2

    except (IndicatorComputationError, FairScoreComputationError) as e:
        print(f"Evaluation error: {e}", file=sys.stderr)
        return 3

    except FileNotFoundError:
        print(f"File not found: {args.input}", file=sys.stderr)
        return 4

    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1
