from pathlib import Path

from scripts.bump_versao import atualizar_pyproject, promover_changelog, proxima_versao
from scripts.changelog import extrair_secao


def test_proxima_versao():
    assert proxima_versao("1.2.3", "patch") == "1.2.4"
    assert proxima_versao("1.2.3", "minor") == "1.3.0"
    assert proxima_versao("1.2.3", "major") == "2.0.0"


def test_bump_move_unreleased(tmp_path: Path):
    pyproject = tmp_path / "pyproject.toml"
    changelog = tmp_path / "CHANGELOG.md"
    pyproject.write_text('[project]\nversion = "1.0.0"\n', encoding="utf-8")
    changelog.write_text("## [Unreleased]\n\n### Added\n\n- novidade\n", encoding="utf-8")
    atualizar_pyproject(pyproject, "1.1.0")
    promover_changelog(changelog, "1.1.0", "2025-01-01")
    assert 'version = "1.1.0"' in pyproject.read_text()
    assert "## [1.1.0] - 2025-01-01" in changelog.read_text()


def test_extrator_changelog():
    conteudo = "## [Unreleased]\n\nx\n\n## [0.2.0] - 2024-01-01\n\nstreaming\n"
    assert extrair_secao(conteudo, "0.2.0") == "## [0.2.0] - 2024-01-01\n\nstreaming"


def test_extrator_changelog_ausente_falha_por_padrao():
    try:
        extrair_secao("## [Unreleased]\n", "9.9.9")
    except ValueError as erro:
        assert "9.9.9" in str(erro)
    else:
        raise AssertionError("seção ausente deveria falhar no modo estrito")


def test_extrator_changelog_ausente_usa_nota_generica():
    notas = extrair_secao(
        "## [Unreleased]\n",
        "9.9.9",
        se_ausente_usar_generico=True,
        repositorio="exemplo/projeto",
    )
    assert "Release v9.9.9" in notas
    assert "https://github.com/exemplo/projeto/compare/main...v9.9.9" in notas
