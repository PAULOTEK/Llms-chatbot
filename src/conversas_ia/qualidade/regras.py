from dataclasses import dataclass
from typing import Any

import yaml


@dataclass(frozen=True)
class Regra:
    nome: str
    tipo: str
    coluna: str
    severidade: str = "critica"
    valores: list[Any] | None = None
    minimo: float | None = None
    maximo: float | None = None
    padrao: str | None = None


def carregar_regras(caminho: str) -> list[Regra]:
    with open(caminho, encoding="utf-8") as arquivo:
        return [Regra(**item) for item in yaml.safe_load(arquivo)["regras"]]
