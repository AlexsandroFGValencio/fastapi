from typing import List, Dict
from src.capital_gains.domain.entities import Portfolio, BuyOperation, SellOperation


class CapitalGainService:
    """Service to calculate taxes for a sequence of buy/sell operations."""

    OPERATION_MAP = {
        "buy": BuyOperation,
        "sell": SellOperation,
    }

    def __init__(self, portfolio: Portfolio | None = None):
        self.portfolio = portfolio or Portfolio()

    def calculate_taxes(self, operations: List[Dict]) -> List[Dict[str, float]]:
        """Calculate the tax for each operation in the given list."""
        results: List[Dict[str, float]] = []

        for op in operations:
            operation_class = self.OPERATION_MAP[op["operation"]]
            operation = operation_class(op["unit-cost"], op["quantity"])
            tax = operation.apply(self.portfolio)
            results.append({"tax": tax})

        return results