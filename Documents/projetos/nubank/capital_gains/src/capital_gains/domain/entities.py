from abc import ABC, abstractmethod

class Operation(ABC):
    """Represents a buy or sell operation."""

    def __init__(self, unit_cost: float, quantity: int):
        self.unit_cost = unit_cost
        self.quantity = quantity

    @abstractmethod
    def apply(self, portfolio) -> float:
        """Apply the operation to the portfolio and return the tax owed, if any."""
        pass


class BuyOperation(Operation):
    def apply(self, portfolio) -> float:
        portfolio.buy(self.unit_cost, self.quantity)
        return 0.0


class SellOperation(Operation):
    def apply(self, portfolio) -> float:
        return portfolio.sell(self.unit_cost, self.quantity)


class Portfolio:
    """Handles buy/sell operations and calculates income tax when applicable."""

    TAX_RATE = 0.2
    TAX_FREE_LIMIT = 20000.0

    def __init__(self):
        self.total_shares = 0
        self.weighted_avg_price = 0.0
        self.accumulated_loss = 0.0

    def buy(self, unit_cost: float, quantity: int):
        total_cost = (self.total_shares * self.weighted_avg_price) + (unit_cost * quantity)
        self.total_shares += quantity
        self.weighted_avg_price = round(total_cost / self.total_shares, 2)

    def sell(self, unit_cost: float, quantity: int) -> float:
        total_sale = unit_cost * quantity
        total_cost = self.weighted_avg_price * quantity
        profit = total_sale - total_cost

        self.total_shares -= quantity

        # Tax-free sale
        if total_sale <= self.TAX_FREE_LIMIT:
            if profit < 0:
                self.accumulated_loss += abs(profit)
            return 0.0

        # No profit
        if profit <= 0:
            if profit < 0:
                self.accumulated_loss += abs(profit)
            return 0.0

        # Taxable profit after accumulated losses
        taxable_profit = max(profit - self.accumulated_loss, 0.0)
        self.accumulated_loss = max(self.accumulated_loss - profit, 0.0)

        return round(taxable_profit * self.TAX_RATE, 2)