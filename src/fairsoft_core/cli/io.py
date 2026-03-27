import json
from pathlib import Path
from typing import Any


def load_json_file(path: str | Path) -> dict[str, Any]:
    input_path = Path(path)
    with input_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def select_output_payload(data: dict[str, Any], selection: str) -> Any:
    if selection == "full":
        return data
    if selection == "result":
        return data.get("result")
    if selection == "logs":
        return data.get("logs")
    if selection == "feedback":
        return data.get("feedback")
    raise ValueError(f"Unsupported output selection: {selection}")


def render_output(data: Any, output_format: str) -> str:
    if output_format == "json":
        return json.dumps(data, indent=2, ensure_ascii=False)
    if output_format == "json-compact":
        return json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    raise ValueError(f"Unsupported output format: {output_format}")


def write_output(rendered: str, output: str | None = None) -> None:
    if output:
        Path(output).write_text(rendered, encoding="utf-8")
    else:
        print(rendered)
