import json
import subprocess
import sys
import unittest
from pathlib import Path
from dataclasses import dataclass
from typing import Any


SCRIPT_PATH = Path(__file__).resolve().parent.parent / "src/main.py"


@dataclass
class ScriptResult:
    stdout_lines: list[str]
    stderr: str
    returncode: int

    @property
    def parsed_output(self) -> list[Any]:
        """Try to parse stdout lines as JSON."""
        try:
            return [json.loads(line) for line in self.stdout_lines]
        except json.JSONDecodeError:
            return []


class ScriptRunner:
    def __init__(self, script_path: Path):
        self.script_path = script_path

    def run_with_stdin(self, stdin_input: str) -> ScriptResult:
        process = subprocess.run(
            [sys.executable, str(self.script_path)],
            input=stdin_input,
            text=True,
            capture_output=True,
            check=False,
        )
        return ScriptResult(
            stdout_lines=process.stdout.strip().splitlines(),
            stderr=process.stderr,
            returncode=process.returncode,
        )


class CapitalGainValidator:
    @staticmethod
    def assert_output_matches(
        testcase: unittest.TestCase,
        result: ScriptResult,
        expected_lines: list[str],
    ):
        testcase.assertEqual(
            result.returncode,
            0,
            msg=(
                f"Script failed with code {result.returncode}\n"
                f"STDERR:\n{result.stderr}\nSTDOUT:\n{result.stdout_lines}"
            ),
        )
        testcase.assertEqual(
            result.stdout_lines,
            expected_lines,
            msg=(
                f"\nMismatched output!\n"
                f"Expected: {expected_lines}\nGot:      {result.stdout_lines}\n"
                f"STDERR: {result.stderr}\n"
            ),
        )


class TestCapitalGain(unittest.TestCase):
    runner = ScriptRunner(SCRIPT_PATH)

    test_cases = [
        # Copiei todos os cenários do seu script original
        (
            json.dumps([
                {'operation': 'buy', 'unit-cost': 10.00, 'quantity': 100},
                {'operation': 'sell', 'unit-cost': 15.00, 'quantity': 50},
                {'operation': 'sell', 'unit-cost': 15.00, 'quantity': 50},
            ]) + "\n",
            [json.dumps([
                {"tax": 0.0},
                {"tax": 0.0},
                {"tax": 0.0},
            ])]
        ),
        (
            json.dumps([
                {'operation': 'buy', 'unit-cost': 10.00, 'quantity': 10000},
                {'operation': 'sell', 'unit-cost': 20.00, 'quantity': 5000},
                {'operation': 'sell', 'unit-cost': 5.00, 'quantity': 5000},
            ]) + "\n",
            [json.dumps([
                {"tax": 0.0},
                {"tax": 10000.0},
                {"tax": 0.0},
            ])]
        ),
        (
            json.dumps([
                {'operation': 'buy', 'unit-cost': 10.00, 'quantity': 100},
                {'operation': 'sell', 'unit-cost': 15.00, 'quantity': 50},
                {'operation': 'sell', 'unit-cost': 15.00, 'quantity': 50},
            ]) + "\n",
            [json.dumps([
                {"tax": 0.0},
                {"tax": 0.0},
                {"tax": 0.0},
            ])]
        ),
        (
            json.dumps([
                {'operation': 'buy', 'unit-cost': 10.00, 'quantity': 10000},
                {'operation': 'sell', 'unit-cost': 20.00, 'quantity': 5000},
                {'operation': 'sell', 'unit-cost': 5.00, 'quantity': 5000},
            ]) + "\n",
            [json.dumps([
                {"tax": 0.0},
                {"tax": 10000.0},
                {"tax": 0.0},
            ])]
        ),
        (
            json.dumps([
                {'operation': 'buy', 'unit-cost': 10.00, 'quantity': 10000},
                {'operation': 'sell', 'unit-cost': 5.00, 'quantity': 5000},
                {'operation': 'sell', 'unit-cost': 20.00, 'quantity': 3000},
            ]) + "\n",
            [json.dumps([
                {"tax": 0.0},
                {"tax": 0.0},
                {"tax": 1000.0},
            ])]
        ),
        (
            json.dumps([
                {'operation': 'buy', 'unit-cost': 10.00, 'quantity': 10000},
                {'operation': 'buy', 'unit-cost': 25.00, 'quantity': 5000},
                {'operation': 'sell', 'unit-cost': 15.00, 'quantity': 10000},
            ]) + "\n",
            [json.dumps([
                {"tax": 0.0},
                {"tax": 0.0},
                {"tax": 0.0},
            ])]
        ),
        (
            json.dumps([
                {'operation': 'buy', 'unit-cost': 10.00, 'quantity': 10000},
                {'operation': 'buy', 'unit-cost': 25.00, 'quantity': 5000},
                {'operation': 'sell', 'unit-cost': 15.00, 'quantity': 10000},
                {'operation': 'sell', 'unit-cost': 25.00, 'quantity': 5000},
            ]) + "\n",
            [json.dumps([
                {"tax": 0.0},
                {"tax": 0.0},
                {"tax": 0.0},
                {"tax": 10000.0},
            ])]
        ),
        (
            json.dumps([
                {'operation': 'buy', 'unit-cost': 10.00, 'quantity': 10000},
                {'operation': 'sell', 'unit-cost': 2.00, 'quantity': 5000},
                {'operation': 'sell', 'unit-cost': 20.00, 'quantity': 2000},
                {'operation': 'sell', 'unit-cost': 20.00, 'quantity': 2000},
                {'operation': 'sell', 'unit-cost': 25.00, 'quantity': 1000},
            ]) + "\n",
            [json.dumps([
                {"tax": 0.0},
                {"tax": 0.0},
                {"tax": 0.0},
                {"tax": 0.0},
                {"tax": 3000.0},
            ])]
        ),
        (
            json.dumps([
                {'operation': 'buy', 'unit-cost': 10.00, 'quantity': 10000},
                {'operation': 'sell', 'unit-cost': 2.00, 'quantity': 5000},
                {'operation': 'sell', 'unit-cost': 20.00, 'quantity': 2000},
                {'operation': 'sell', 'unit-cost': 20.00, 'quantity': 2000},
                {'operation': 'sell', 'unit-cost': 25.00, 'quantity': 1000},
                {'operation': 'buy', 'unit-cost': 20.00, 'quantity': 10000},
                {'operation': 'sell', 'unit-cost': 15.00, 'quantity': 5000},
                {'operation': 'sell', 'unit-cost': 30.00, 'quantity': 4350},
                {'operation': 'sell', 'unit-cost': 30.00, 'quantity': 650},
            ]) + "\n",
            [json.dumps([
                {"tax": 0.0},
                {"tax": 0.0},
                {"tax": 0.0},
                {"tax": 0.0},
                {"tax": 3000.0},
                {"tax": 0.0},
                {"tax": 0.0},
                {"tax": 3700.0},
                {"tax": 0.0},
            ])]
        ),
        (
            json.dumps([
                {'operation': 'buy', 'unit-cost': 10.00, 'quantity': 10000},
                {'operation': 'sell', 'unit-cost': 50.00, 'quantity': 10000},
                {'operation': 'buy', 'unit-cost': 20.00, 'quantity': 10000},
                {'operation': 'sell', 'unit-cost': 50.00, 'quantity': 10000},
            ]) + "\n",
            [json.dumps([
                {"tax": 0.0},
                {"tax": 80000.0},
                {"tax": 0.0},
                {"tax": 60000.0},
            ])]
        ),
        (
            json.dumps([
                {'operation': 'buy', 'unit-cost': 5000.00, 'quantity': 10},
                {'operation': 'sell', 'unit-cost': 4000.00, 'quantity': 5},
                {'operation': 'buy', 'unit-cost': 15000.00, 'quantity': 5},
                {'operation': 'buy', 'unit-cost': 4000.00, 'quantity': 2},
                {'operation': 'buy', 'unit-cost': 23000.00, 'quantity': 2},
                {'operation': 'sell', 'unit-cost': 20000.00, 'quantity': 1},
                {'operation': 'sell', 'unit-cost': 12000.00, 'quantity': 10},
                {'operation': 'sell', 'unit-cost': 15000.00, 'quantity': 3},
            ]) + "\n",
            [json.dumps([
                {"tax": 0.0},
                {"tax": 0.0},
                {"tax": 0.0},
                {"tax": 0.0},
                {"tax": 0.0},
                {"tax": 0.0},
                {"tax": 1000.0},
                {"tax": 2400.0},
            ])]
        ),
    ]

    def test_all_cases(self):
        for stdin_input, expected_lines in self.test_cases:
            with self.subTest(stdin_input=stdin_input[:50]):
                result = self.runner.run_with_stdin(stdin_input)
                CapitalGainValidator.assert_output_matches(self, result, expected_lines)


if __name__ == "__main__":
    unittest.main()