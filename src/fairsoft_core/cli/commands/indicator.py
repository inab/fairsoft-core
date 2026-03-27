import sys
from typing import Any, Callable

from fairsoft_core.cli.io import (
    load_json_file,
    render_output,
    select_output_payload,
    write_output,
)
from fairsoft_core.exceptions import InstanceCreationError
from fairsoft_core.indicators.a_indicators import (
    compA1_1,
    compA1_2,
    compA1_3,
    compA1_4,
    compA1_5,
    compA3_1,
    compA3_2,
    compA3_3,
    compA3_4,
    compA3_5,
)
from fairsoft_core.indicators.f_indicators import (
    compF1_2,
    compF2_1,
    compF2_2,
    compF3_1,
    compF3_2,
    compF3_3,
)
from fairsoft_core.indicators.i_indicators import (
    compI1_1,
    compI1_2,
    compI1_3,
    compI1_4,
    compI2_1,
    compI2_2,
    compI3_1,
    compI3_2,
    compI3_3,
)
from fairsoft_core.indicators.r_indicators import (
    compR1_1,
    compR2_1,
    compR2_2,
    compR3_1,
    compR3_2,
    compR4_1,
    compR4_2,
)
from fairsoft_core.inputs import normalize_input
from fairsoft_core.models.instance import Instance

IndicatorFunc = Callable[[Instance], tuple[bool, list[str]]]


AVAILABLE_INDICATORS: dict[str, dict[str, Any]] = {
    "A1_1": {
        "name": "existence_of_api_or_web",
        "description": "Existence of API or web.",
        "function": compA1_1,
        "fields_used": ["webpage", "type"],
        "minimum_metadata": "webpage",
        "not_applicable_when": "super_type == 'no_web'",
        "notes": "Checks whether at least one webpage/API URL is operational.",
    },
    "A1_2": {
        "name": "downloadable_and_buildable_working_version",
        "description": "Existence of downloadable and buildable software working version.",
        "function": compA1_2,
        "fields_used": ["download", "src", "type"],
        "minimum_metadata": "download or src",
        "not_applicable_when": "super_type == 'web'",
        "notes": "Checks whether at least one download or source URL is operational.",
    },
    "A1_3": {
        "name": "installation_instructions",
        "description": "Existence of installation instructions.",
        "function": compA1_3,
        "fields_used": ["inst_instr", "documentation", "source", "type"],
        "minimum_metadata": "inst_instr or documentation or source",
        "not_applicable_when": "super_type == 'web'",
        "notes": "Can pass through explicit flag, matching documentation, or known sources that provide installation instructions.",
    },
    "A1_4": {
        "name": "test_data",
        "description": "Existence of test data.",
        "function": compA1_4,
        "fields_used": ["test", "documentation", "type"],
        "minimum_metadata": "test or documentation",
        "not_applicable_when": "super_type == 'web'",
        "notes": "Checks explicit test data URLs first, then documentation entries of type 'test data'.",
    },
    "A1_5": {
        "name": "source_code",
        "description": "Existence of software source code.",
        "function": compA1_5,
        "fields_used": ["src", "type"],
        "minimum_metadata": "src",
        "not_applicable_when": "super_type == 'web'",
        "notes": "Requires at least one operational source-code URL.",
    },
    "A3_1": {
        "name": "registration_not_compulsory",
        "description": "Registration not compulsory.",
        "function": compA3_1,
        "fields_used": ["registration_not_mandatory"],
        "minimum_metadata": "registration_not_mandatory",
        "not_applicable_when": None,
        "notes": "Passes only when registration_not_mandatory is true.",
    },
    "A3_2": {
        "name": "version_for_free_os",
        "description": "Availability of version for free OS.",
        "function": compA3_2,
        "fields_used": ["os", "type"],
        "minimum_metadata": "os",
        "not_applicable_when": "super_type == 'web'",
        "notes": "Checks whether at least one OS belongs to the list of free operating systems.",
    },
    "A3_3": {
        "name": "availability_for_several_os",
        "description": "Availability for several OS.",
        "function": compA3_3,
        "fields_used": ["os", "type"],
        "minimum_metadata": "os",
        "not_applicable_when": "super_type == 'web'",
        "notes": "Passes when more than one OS is listed.",
    },
    "A3_4": {
        "name": "availability_on_free_e_infrastructures",
        "description": "Availability on free e-Infrastructures.",
        "function": compA3_4,
        "fields_used": ["e_infrastructures", "webpage", "source", "type"],
        "minimum_metadata": "e_infrastructures or webpage or source",
        "not_applicable_when": "super_type == 'web'",
        "notes": "Checks e-infrastructures explicitly, then webpage URLs, then known source values.",
    },
    "A3_5": {
        "name": "availability_on_several_e_infrastructures",
        "description": "Availability on several e-Infrastructures.",
        "function": compA3_5,
        "fields_used": ["e_infrastructures", "webpage", "source", "type"],
        "minimum_metadata": "e_infrastructures or webpage or source",
        "not_applicable_when": "super_type == 'web'",
        "notes": "Passes when more than one e-infrastructure is found explicitly, in URLs, or in sources.",
    },
    "F1_2": {
        "name": "semantic_versioning",
        "description": "Semantic versioning.",
        "function": compF1_2,
        "fields_used": ["version"],
        "minimum_metadata": "version",
        "not_applicable_when": None,
        "notes": "Checks whether version strings follow a simplified semantic-versioning pattern.",
    },
    "F2_1": {
        "name": "structured_metadata",
        "description": "Structured metadata.",
        "function": compF2_1,
        "fields_used": ["source"],
        "minimum_metadata": "source",
        "not_applicable_when": None,
        "notes": "Passes if at least one source belongs to the structured-metadata sources list.",
    },
    "F2_2": {
        "name": "metadata_with_controlled_vocabularies",
        "description": "Software described using ontologies or controlled vocabularies.",
        "function": compF2_2,
        "fields_used": ["topics", "operations"],
        "minimum_metadata": "topics or operations",
        "not_applicable_when": None,
        "notes": "Passes if at least one topic or operation includes a vocabulary.",
    },
    "F3_1": {
        "name": "searchability_in_registries",
        "description": "Searchability in registries.",
        "function": compF3_1,
        "fields_used": ["source", "registries"],
        "minimum_metadata": "source or registries",
        "not_applicable_when": None,
        "notes": "Passes if at least one known software registry is found in source or registries.",
    },
    "F3_2": {
        "name": "searchability_in_software_repositories",
        "description": "Searchability in software repositories.",
        "function": compF3_2,
        "fields_used": ["repository"],
        "minimum_metadata": "repository",
        "not_applicable_when": None,
        "notes": "Requires at least one repository URL and checks whether it is operational.",
    },
    "F3_3": {
        "name": "searchability_in_literature",
        "description": "Searchability in literature.",
        "function": compF3_3,
        "fields_used": ["publication"],
        "minimum_metadata": "publication",
        "not_applicable_when": None,
        "notes": "Passes if at least one publication entry is present.",
    },
    "I1_1": {
        "name": "standard_data_formats",
        "description": "Usage of standard data formats.",
        "function": compI1_1,
        "fields_used": ["input", "output"],
        "minimum_metadata": "input or output",
        "not_applicable_when": None,
        "notes": "Passes if at least one input or output format has a vocabulary.",
    },
    "I1_2": {
        "name": "api_standard_specification",
        "description": "API standard specification.",
        "function": compI1_2,
        "fields_used": ["documentation", "type"],
        "minimum_metadata": "documentation",
        "not_applicable_when": "super_type == 'no_web'",
        "notes": "Looks for documentation entries of type 'API specification' with operational URLs.",
    },
    "I1_3": {
        "name": "verifiable_data_formats",
        "description": "Verificability of data formats.",
        "function": compI1_3,
        "fields_used": ["input", "output"],
        "minimum_metadata": "input or output",
        "not_applicable_when": None,
        "notes": "Checks whether at least one input or output term belongs to the verifiable-formats list.",
    },
    "I1_4": {
        "name": "flexibility_of_supported_data_formats",
        "description": "Flexibility of data format supported.",
        "function": compI1_4,
        "fields_used": ["input", "output"],
        "minimum_metadata": "input and output",
        "not_applicable_when": None,
        "notes": "Passes when more than one input format and more than one output format are listed.",
    },
    "I2_1": {
        "name": "api_or_library_version",
        "description": "Existence of API/library version.",
        "function": compI2_1,
        "fields_used": ["type"],
        "minimum_metadata": "type",
        "not_applicable_when": None,
        "notes": "Passes when the software type includes lib, rest, soap, or api.",
    },
    "I2_2": {
        "name": "e_infrastructure_compatibility",
        "description": "E-infrastructure compatibility.",
        "function": compI2_2,
        "fields_used": ["e_infrastructures", "webpage", "source"],
        "minimum_metadata": "e_infrastructures or webpage or source",
        "not_applicable_when": None,
        "notes": "Checks explicit e-infrastructures first, then matching webpage URLs, then known source values.",
    },
    "I3_1": {
        "name": "dependencies_statement",
        "description": "Dependencies statement.",
        "function": compI3_1,
        "fields_used": ["dependencies"],
        "minimum_metadata": "dependencies",
        "not_applicable_when": None,
        "notes": "Passes if dependencies are listed.",
    },
    "I3_2": {
        "name": "dependencies_provided",
        "description": "Dependencies are provided.",
        "function": compI3_2,
        "fields_used": ["source", "registries", "links"],
        "minimum_metadata": "source or registries or links",
        "not_applicable_when": None,
        "notes": "Checks whether dependencies-aware systems are referenced through sources, registries, or links.",
    },
    "I3_3": {
        "name": "dependency_aware_system",
        "description": "Dependency-aware system.",
        "function": compI3_3,
        "fields_used": ["source", "registries", "links"],
        "minimum_metadata": "source or registries or links",
        "not_applicable_when": None,
        "notes": "Currently delegates to I3_2.",
    },
    "R1_1": {
        "name": "usage_guides",
        "description": "Existence of usage guides.",
        "function": compR1_1,
        "fields_used": ["documentation"],
        "minimum_metadata": "documentation",
        "not_applicable_when": None,
        "notes": "Passes if at least one documentation entry is considered a usage guide and its URL is operational.",
    },
    "R2_1": {
        "name": "license",
        "description": "Existence of license.",
        "function": compR2_1,
        "fields_used": ["license", "documentation"],
        "minimum_metadata": "license or documentation",
        "not_applicable_when": None,
        "notes": "Checks explicit licenses first, then documentation matching valid permissions/license types.",
    },
    "R2_2": {
        "name": "technical_conditions_of_use",
        "description": "Technical conditions of use.",
        "function": compR2_2,
        "fields_used": ["license", "documentation"],
        "minimum_metadata": "license or documentation",
        "not_applicable_when": None,
        "notes": "Currently delegates to R2_1.",
    },
    "R3_1": {
        "name": "contribution_policy",
        "description": "Contribution policy.",
        "function": compR3_1,
        "fields_used": ["documentation"],
        "minimum_metadata": "documentation",
        "not_applicable_when": None,
        "notes": "Looks for documentation whose type matches contribution-policy types and has an operational URL.",
    },
    "R3_2": {
        "name": "credit",
        "description": "Existence of credit.",
        "function": compR3_2,
        "fields_used": ["authors"],
        "minimum_metadata": "authors",
        "not_applicable_when": None,
        "notes": "Passes if at least one author is listed.",
    },
    "R4_1": {
        "name": "public_version_control",
        "description": "Usage of (public) version control.",
        "function": compR4_1,
        "fields_used": ["version_control"],
        "minimum_metadata": "version_control",
        "not_applicable_when": None,
        "notes": "Passes when version_control is true.",
    },
    "R4_2": {
        "name": "release_policy",
        "description": "Release policy.",
        "function": compR4_2,
        "fields_used": ["documentation"],
        "minimum_metadata": "documentation",
        "not_applicable_when": None,
        "notes": "Looks for documentation whose type matches release-policy types and has an operational URL.",
    },
}


def _build_indicator_aliases() -> dict[str, str]:
    aliases: dict[str, str] = {}
    for indicator_id, spec in AVAILABLE_INDICATORS.items():
        aliases[indicator_id.lower()] = indicator_id
        aliases[spec["name"].lower()] = indicator_id
    return aliases


INDICATOR_ALIASES = _build_indicator_aliases()


def _resolve_indicator(indicator_value: str | None) -> str | None:
    if indicator_value is None:
        return None
    return INDICATOR_ALIASES.get(indicator_value.lower())


def _list_available_indicators() -> str:
    lines = ["Available indicators:"]
    for indicator_id, spec in AVAILABLE_INDICATORS.items():
        lines.append(f"  - {indicator_id}: {spec['name']}")
        lines.append(f"    Description: {spec['description']}")
        lines.append(f"    Fields used: {', '.join(spec['fields_used'])}")
        lines.append(f"    Minimum metadata: {spec['minimum_metadata']}")
        if spec["not_applicable_when"]:
            lines.append(f"    Not applicable when: {spec['not_applicable_when']}")
    return "\n".join(lines)


def _describe_indicator(indicator_id: str) -> str:
    spec = AVAILABLE_INDICATORS[indicator_id]
    lines = [
        f"{indicator_id} — {spec['name']}",
        f"Description: {spec['description']}",
        f"Fields used: {', '.join(spec['fields_used'])}",
        f"Minimum metadata: {spec['minimum_metadata']}",
    ]
    if spec["not_applicable_when"]:
        lines.append(f"Not applicable when: {spec['not_applicable_when']}")
    if spec.get("notes"):
        lines.append(f"Notes: {spec['notes']}")
    return "\n".join(lines)


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

        if args.describe:
            resolved = _resolve_indicator(args.describe)
            if not resolved:
                print(
                    f"Unknown indicator '{args.describe}'. Use 'fairsoft indicator --list' to see available indicators.",
                    file=sys.stderr,
                )
                return 2
            print(_describe_indicator(resolved))
            return 0

        if not args.indicator:
            print(
                "Error: missing indicator. Use 'fairsoft indicator --list' to see available indicators.",
                file=sys.stderr,
            )
            return 2

        if not args.input:
            print("Error: missing input file.", file=sys.stderr)
            return 2

        resolved_indicator = _resolve_indicator(args.indicator)
        if not resolved_indicator:
            print(
                f"Unknown indicator '{args.indicator}'. Use 'fairsoft indicator --list' to see available indicators.",
                file=sys.stderr,
            )
            return 2

        raw_data = load_json_file(args.input)
        tool_metadata = normalize_input(raw_data, args.input_format)

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