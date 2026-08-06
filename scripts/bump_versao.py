"""Atualiza a versão SemVer e promove o conteúdo Unreleased."""

import argparse
import datetime
import re
from pathlib import Path


def proxima_versao(atual: str, tipo: str) -> str:
    major, minor, patch = (int(parte) for parte in atual.split("."))
    if tipo == "major":
        return f"{major + 1}.0.0"
    if tipo == "minor":
        return f"{major}.{minor + 1}.0"
    if tipo == "patch":
        return f"{major}.{minor}.{patch + 1}"
    raise ValueError("tipo deve ser patch, minor ou major")


def atualizar_pyproject(caminho: Path, nova: str) -> None:
    conteudo = caminho.read_text(encoding="utf-8")
    atualizado, ocorrencias = re.subn(
        r'(?m)^(version\s*=\s*)"[^"]+"$', rf'\1"{nova}"', conteudo, count=1
    )
    if ocorrencias != 1:
        raise ValueError("Campo project.version não encontrado no pyproject.toml")
    caminho.write_text(atualizado, encoding="utf-8")


def promover_changelog(caminho: Path, nova: str, data: str | None = None) -> None:
    conteudo = caminho.read_text(encoding="utf-8")
    marcador = re.search(r"^## \[Unreleased\]\s*$", conteudo, re.MULTILINE)
    if not marcador:
        raise ValueError("Seção [Unreleased] não encontrada no CHANGELOG.")
    proxima = re.search(r"^## \[", conteudo[marcador.end() :], re.MULTILINE)
    fim = marcador.end() + proxima.start() if proxima else len(conteudo)
    corpo = conteudo[marcador.end() : fim].strip()
    data = data or datetime.date.today().isoformat()
    nova_secao = f"## [{nova}] - {data}\n\n{corpo}\n\n" if corpo else f"## [{nova}] - {data}\n\n"
    atualizado = conteudo[: marcador.end()] + "\n\n" + nova_secao + conteudo[fim:]
    caminho.write_text(atualizado, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("tipo", choices=["patch", "minor", "major"])
    parser.add_argument("--pyproject", default="pyproject.toml")
    parser.add_argument("--changelog", default="CHANGELOG.md")
    args = parser.parse_args()
    pyproject = Path(args.pyproject)
    import tomllib

    atual = tomllib.loads(pyproject.read_text(encoding="utf-8"))["project"]["version"]
    nova = proxima_versao(atual, args.tipo)
    atualizar_pyproject(pyproject, nova)
    promover_changelog(Path(args.changelog), nova)
    print(f"{atual} -> {nova}")


if __name__ == "__main__":
    main()
