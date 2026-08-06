from pathlib import Path
from typing import Any

import yaml


def carregar_yaml(caminho: str | Path) -> dict[str, Any]:
    with Path(caminho).open(encoding="utf-8") as arquivo:
        return yaml.safe_load(arquivo) or {}


def carregar_ambiente(caminho: str | Path, ambiente: str) -> dict[str, Any]:
    return carregar_yaml(caminho)[ambiente]
