from fairsoft_core.inputs.codemeta import load_codemeta_metadata
from fairsoft_core.inputs.native_json import load_native_metadata


def normalize_input(data: dict, input_format: str) -> dict:
    if input_format == "native":
        return load_native_metadata(data)
    if input_format == "codemeta":
        return load_codemeta_metadata(data)
    raise ValueError(f"Unsupported input format: {input_format}")
