from pyspark.sql import Column
from pyspark.sql import functions as F

PADROES = {
    # CPF exige pontuação para não confundir telefone nacional de 11 dígitos.
    "cpf": r"\b\d{3}[.\s]\d{3}[.\s]\d{3}[-\s]\d{2}\b",
    "email": r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}",
    "telefone": r"(?<!\d)(?:\+?55\s?)?(?:\(?\d{2}\)?\s?)?9?\d{4}[-\s]?\d{4}(?!\d)",
    "cnpj": r"\b\d{2}[.\s]?\d{3}[.\s]?\d{3}[/\s]?\d{4}[-\s]?\d{2}\b",
    "cartao": r"\b(?:\d[ -]?){13,19}\b",
}


def detectar_tipos(coluna: Column) -> Column:
    encontrados = [F.when(coluna.rlike(regex), F.lit(tipo)) for tipo, regex in PADROES.items()]
    return F.filter(F.array(*encontrados), lambda item: item.isNotNull())


def coluna_tem_pii(coluna: Column) -> Column:
    return F.size(detectar_tipos(coluna)) > 0
