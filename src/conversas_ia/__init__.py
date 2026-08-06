"""Lakehouse conversacional para preparação de dados de IA."""

from importlib.metadata import PackageNotFoundError, version
from pathlib import Path


def _versao_fallback() -> str:
    try:
        import tomllib

        caminho = Path(__file__).resolve().parents[2] / "pyproject.toml"
        return tomllib.loads(caminho.read_text(encoding="utf-8"))["project"]["version"]
    except (FileNotFoundError, KeyError, TypeError):
        return "desconhecida"


try:
    __version__ = version("conversas-ia")
except PackageNotFoundError:
    __version__ = _versao_fallback()

__all__ = ["__version__"]
