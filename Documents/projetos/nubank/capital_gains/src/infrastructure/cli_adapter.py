import sys
import json
from src.capital_gains.domain.services import CapitalGainService


class CLIAdapter:
    """Command-line adapter to execute the CapitalGainService using stdin/stdout."""

    def __init__(self, service: CapitalGainService):
        self.service = service

    def run(self) -> None:
        """Read operations from stdin, calculate taxes, and print the results as JSON."""
        raw_input = sys.stdin.read().strip()
        if not raw_input:
            return

        operations = json.loads(raw_input)
        taxes = self.service.calculate_taxes(operations)
        print(json.dumps(taxes))