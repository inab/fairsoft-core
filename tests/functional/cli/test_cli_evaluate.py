# tests/test_cli_evaluate.py

import json
import sys
from pathlib import Path

from fairsoft_core.cli.main import main

VALID_EVALUATION_INPUT = {
    "name": "Flower",
    "type": ["lib"],
    "repository": ["https://github.com/adap/flower"],
    "version_control": True,
}


def write_json(tmp_path: Path, name: str, payload: dict) -> Path:
    path = tmp_path / name
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def run_cli(args, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["fairsoft", *args])
    return main()


def test_evaluate_full(tmp_path, capsys, monkeypatch):
    input_file = write_json(tmp_path, "input.json", VALID_EVALUATION_INPUT)

    exit_code = run_cli(["evaluate", str(input_file)], monkeypatch)

    captured = capsys.readouterr()
    assert exit_code == 0

    print(captured.out)

    data = json.loads(captured.out)
    assert "result" in data
    assert "logs" in data
    assert "feedback" in data


def test_evaluate_select_result(tmp_path, capsys, monkeypatch):
    input_file = write_json(tmp_path, "input.json", VALID_EVALUATION_INPUT)

    exit_code = run_cli(
        ["evaluate", str(input_file), "--select", "result"],
        monkeypatch,
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    result = json.loads(captured.out)
    assert isinstance(result, dict)


def test_evaluate_output_file(tmp_path, capsys, monkeypatch):
    input_file = write_json(tmp_path, "input.json", VALID_EVALUATION_INPUT)
    output_file = tmp_path / "evaluation.json"

    exit_code = run_cli(
        ["evaluate", str(input_file), "--output", str(output_file)],
        monkeypatch,
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out == ""
    assert output_file.exists()
