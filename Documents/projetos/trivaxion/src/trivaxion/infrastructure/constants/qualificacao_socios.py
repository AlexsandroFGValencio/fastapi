"""
Mapeamento de códigos de qualificação de sócios conforme tabela da Receita Federal.

Fonte: Metadados CNPJ - Receita Federal do Brasil
https://www.gov.br/receitafederal/dados/cnpj-metadados.pdf
"""

QUALIFICACAO_SOCIOS = {
    "05": "Administrador",
    "08": "Conselheiro de Administração",
    "10": "Diretor",
    "16": "Presidente",
    "17": "Procurador",
    "20": "Sociedade Consorciada",
    "21": "Sociedade Filiada",
    "22": "Sócio",
    "23": "Sócio Capitalista",
    "24": "Sócio Comanditado",
    "25": "Sócio Comanditário",
    "26": "Sócio de Indústria",
    "28": "Sócio-Gerente",
    "29": "Sócio Incapaz ou Relativamente Incapaz (exceto menor)",
    "30": "Sócio Menor (Assistido/Representado)",
    "31": "Sócio Ostensivo",
    "37": "Sócio Pessoa Jurídica Domiciliado no Exterior",
    "38": "Sócio Pessoa Física Residente ou Domiciliado no Exterior",
    "47": "Sócio Pessoa Física Residente no Brasil",
    "48": "Sócio Pessoa Jurídica Domiciliado no Brasil",
    "49": "Sócio-Administrador",
    "52": "Sócio com Capital",
    "53": "Sócio sem Capital",
    "54": "Fundador",
    "55": "Sócio Comanditado Residente no Exterior",
    "56": "Sócio Comanditário Pessoa Física Residente no Exterior",
    "57": "Sócio Comanditário Pessoa Jurídica Domiciliado no Exterior",
    "58": "Sócio Comanditário Incapaz",
    "59": "Produtor Rural",
    "63": "Cotas em Tesouraria",
    "65": "Titular Pessoa Física Residente ou Domiciliado no Brasil",
    "66": "Titular Pessoa Física Residente ou Domiciliado no Exterior",
    "67": "Titular Pessoa Física Incapaz ou Relativamente Incapaz (exceto menor)",
    "68": "Titular Pessoa Física Menor (Assistido/Representado)",
    "70": "Administrador Residente ou Domiciliado no Exterior",
    "71": "Conselheiro de Administração Residente ou Domiciliado no Exterior",
    "72": "Diretor Residente ou Domiciliado no Exterior",
    "73": "Presidente Residente ou Domiciliado no Exterior",
    "74": "Sócio-Administrador Residente ou Domiciliado no Exterior",
    "75": "Fundador Residente ou Domiciliado no Exterior",
    "76": "Responsável",
    "77": "Responsável Residente ou Domiciliado no Exterior",
    "78": "Assistente",
    "79": "Assistente Residente ou Domiciliado no Exterior",
}


def get_qualificacao_descricao(codigo: str | None) -> str:
    """
    Retorna a descrição da qualificação do sócio a partir do código.
    
    Args:
        codigo: Código de qualificação (ex: "49")
    
    Returns:
        Descrição da qualificação (ex: "Sócio-Administrador")
        Se o código não for encontrado, retorna o próprio código
    """
    if not codigo:
        return "Não informado"
    
    codigo_limpo = str(codigo).strip()
    return QUALIFICACAO_SOCIOS.get(codigo_limpo, f"Código {codigo_limpo}")


def get_qualificacao_completa(codigo: str | None) -> str:
    """
    Retorna a qualificação completa no formato "XX - Descrição".
    
    Args:
        codigo: Código de qualificação (ex: "49")
    
    Returns:
        Qualificação completa (ex: "49 - Sócio-Administrador")
    """
    if not codigo:
        return "Não informado"
    
    codigo_limpo = str(codigo).strip()
    descricao = QUALIFICACAO_SOCIOS.get(codigo_limpo, "Desconhecido")
    return f"{codigo_limpo} - {descricao}"
