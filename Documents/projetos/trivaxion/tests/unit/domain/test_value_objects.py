import pytest

from trivaxion.domain.shared.value_objects import CNPJ, Email


class TestCNPJ:
    def test_valid_cnpj(self) -> None:
        cnpj = CNPJ("11.222.333/0001-81")
        assert cnpj.value == "11222333000181"
    
    def test_invalid_cnpj(self) -> None:
        with pytest.raises(ValueError):
            CNPJ("11.222.333/0001-00")
    
    def test_cnpj_formatting(self) -> None:
        cnpj = CNPJ("11222333000181")
        assert cnpj.formatted() == "11.222.333/0001-81"


class TestEmail:
    def test_valid_email(self) -> None:
        email = Email("user@example.com")
        assert email.value == "user@example.com"
    
    def test_invalid_email(self) -> None:
        with pytest.raises(ValueError):
            Email("invalid-email")
