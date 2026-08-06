"""Extrai uma seção versionada do CHANGELOG."""

import argparse
import re
from pathlib import Path


def extrair_secao(conteudo: str, versao: str) -> str:
    padrao = re.compile(rf"^## \[{re.escape(versao)}\].*$", re.MULTILINE)
    inicio = padrao.search(conteudo)
    if not inicio:
        raise ValueError(f"Seção [{versao}] não encontrada no CHANGELOG.")
    proxima = re.search(r"^## \[", conteudo[inicio.end() :], re.MULTILINE)
    fim = inicio.end() + proxima.start() if proxima else len(conteudo)
    return conteudo[inicio.start() : fim].strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True)
    parser.add_argument("--arquivo", default="CHANGELOG.md")
    args = parser.parse_args()
    print(extrair_secao(Path(args.arquivo).read_text(encoding="utf-8"), args.version))


if __name__ == "__main__":
    main()
