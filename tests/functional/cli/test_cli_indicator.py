import json
import sys
from pathlib import Path

from fairsoft_core.cli.main import main

VALID_F3_1_PASSING_INPUT = {
    "name": "ExampleTool",
    "type": ["cmd"],
    "source": ["biotools"],
}

VALID_F3_1_FAILING_INPUT = {
    "name": "ExampleTool",
    "type": ["cmd"],
    "source": ["random_source"],
    "registries": ["unknown_registry"],
}

INVALID_INPUT = {
    "name": "ExampleTool",
    "type": 123,
}


def write_json(tmp_path: Path, name: str, payload: dict) -> Path:
    path = tmp_path / name
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def run_cli(args, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["fairsoft", *args])
    return main()


def test_indicator_list(capsys, monkeypatch):
    exit_code = run_cli(["indicator", "--list"], monkeypatch)

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Available indicators" in captured.out
    assert "F3_1" in captured.out
    assert "searchability_in_registries" in captured.out


def test_indicator_f3_1_by_id(tmp_path, capsys, monkeypatch):
    input_file = write_json(tmp_path, "input.json", VALID_F3_1_PASSING_INPUT)

    exit_code = run_cli(["indicator", "F3_1", str(input_file)], monkeypatch)

    captured = capsys.readouterr()
    assert exit_code == 0

    data = json.loads(captured.out)
    assert data["result"] is True
    assert isinstance(data["logs"], list)
    assert "feedback" in data


def test_indicator_f3_1_by_name(tmp_path, capsys, monkeypatch):
    input_file = write_json(tmp_path, "input.json", VALID_F3_1_PASSING_INPUT)

    exit_code = run_cli(
        ["indicator", "searchability_in_registries", str(input_file)],
        monkeypatch,
    )

    captured = capsys.readouterr()
    assert exit_code == 0

    data = json.loads(captured.out)
    assert data["result"] is True


def test_indicator_select_result(tmp_path, capsys, monkeypatch):
    input_file = write_json(tmp_path, "input.json", VALID_F3_1_PASSING_INPUT)

    exit_code = run_cli(
        ["indicator", "F3_1", str(input_file), "--select", "result"],
        monkeypatch,
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert json.loads(captured.out) is True


def test_indicator_select_logs(tmp_path, capsys, monkeypatch):
    input_file = write_json(tmp_path, "input.json", VALID_F3_1_PASSING_INPUT)

    exit_code = run_cli(
        ["indicator", "F3_1", str(input_file), "--select", "logs"],
        monkeypatch,
    )

    captured = capsys.readouterr()
    assert exit_code == 0

    logs = json.loads(captured.out)
    assert isinstance(logs, list)
    assert any("registries" in log.lower() for log in logs)


def test_indicator_json_compact(tmp_path, capsys, monkeypatch):
    input_file = write_json(tmp_path, "input.json", VALID_F3_1_PASSING_INPUT)

    exit_code = run_cli(
        [
            "indicator",
            "F3_1",
            str(input_file),
            "--select",
            "result",
            "--format",
            "json-compact",
        ],
        monkeypatch,
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out.strip() == "true"


def test_indicator_output_file(tmp_path, capsys, monkeypatch):
    input_file = write_json(tmp_path, "input.json", VALID_F3_1_PASSING_INPUT)
    output_file = tmp_path / "result.json"

    exit_code = run_cli(
        [
            "indicator",
            "F3_1",
            str(input_file),
            "--output",
            str(output_file),
        ],
        monkeypatch,
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out == ""
    assert output_file.exists()

    data = json.loads(output_file.read_text(encoding="utf-8"))
    assert data["result"] is True


def test_indicator_unknown_indicator(tmp_path, capsys, monkeypatch):
    input_file = write_json(tmp_path, "input.json", VALID_F3_1_PASSING_INPUT)

    exit_code = run_cli(
        ["indicator", "NOT_REAL", str(input_file)],
        monkeypatch,
    )

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "Unknown indicator" in captured.err


def test_indicator_missing_file(capsys, monkeypatch):
    exit_code = run_cli(
        ["indicator", "F3_1", "does_not_exist.json"],
        monkeypatch,
    )

    captured = capsys.readouterr()
    assert exit_code == 4
    assert "File not found" in captured.err


def test_indicator_invalid_input(tmp_path, capsys, monkeypatch):
    input_file = write_json(tmp_path, "input.json", INVALID_INPUT)

    exit_code = run_cli(
        ["indicator", "F3_1", str(input_file)],
        monkeypatch,
    )

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "Input error" in captured.err


def test_indicator_f3_1_false_case(tmp_path, capsys, monkeypatch):
    input_file = write_json(tmp_path, "input.json", VALID_F3_1_FAILING_INPUT)

    exit_code = run_cli(["indicator", "F3_1", str(input_file)], monkeypatch)

    captured = capsys.readouterr()
    assert exit_code == 0

    data = json.loads(captured.out)
    assert data["result"] is False
