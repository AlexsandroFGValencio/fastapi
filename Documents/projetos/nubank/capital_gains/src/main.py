from src.capital_gains.domain.services import CapitalGainService
from src.infrastructure.cli_adapter import CLIAdapter


def main() -> None:
    """Entry point to execute the Capital Gain CLI."""
    service = CapitalGainService()
    cli = CLIAdapter(service)
    cli.run()


if __name__ == "__main__":
    main()