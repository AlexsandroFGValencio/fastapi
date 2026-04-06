from trivaxion.adapters.outbound.providers.receita_federal.models import ReceitaFederalRawData
from trivaxion.application.ports.providers import CompanyData


class ReceitaFederalMapper:
    @staticmethod
    def to_company_data(raw_data: ReceitaFederalRawData) -> CompanyData:
        capital_social = None
        if raw_data.capital_social:
            try:
                capital_str = raw_data.capital_social.replace(".", "").replace(",", ".")
                capital_str = "".join(filter(lambda x: x.isdigit() or x == ".", capital_str))
                capital_social = float(capital_str) if capital_str else None
            except (ValueError, AttributeError):
                capital_social = None

        return CompanyData(
            cnpj=raw_data.cnpj,
            razao_social=raw_data.razao_social or "",
            nome_fantasia=raw_data.nome_fantasia,
            situacao_cadastral=raw_data.situacao_cadastral or "desconhecida",
            data_abertura=raw_data.data_abertura,
            cnae_principal=raw_data.cnae_fiscal,
            cnae_descricao=raw_data.cnae_fiscal_descricao,
            natureza_juridica=raw_data.natureza_juridica,
            logradouro=raw_data.logradouro,
            numero=raw_data.numero,
            complemento=raw_data.complemento,
            bairro=raw_data.bairro,
            municipio=raw_data.municipio,
            uf=raw_data.uf,
            cep=raw_data.cep,
            capital_social=capital_social,
            porte=raw_data.porte,
            socios=raw_data.socios,
        )
