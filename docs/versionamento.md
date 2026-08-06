# Versionamento e releases

## Política

O projeto segue SemVer (`MAJOR.MINOR.PATCH`) e mantém uma única fonte de
verdade em `pyproject.toml`. O pacote expõe a mesma versão em
`conversas_ia.__version__`. O `CHANGELOG.md` segue Keep a Changelog.

- `PATCH`: correção compatível.
- `MINOR`: funcionalidade compatível.
- `MAJOR`: alteração incompatível.

Commits devem preferir Conventional Commits (`feat:`, `fix:`, `docs:`,
`refactor:`, `test:`, `chore:`). Branches usam
`devin/<timestamp>-<tema>`, por exemplo `devin/1786022028-versionamento`.

## Fluxo de release

1. Altere o código e registre a mudança em `Unreleased`.
2. Execute `make bump-patch`, `make bump-minor` ou `make bump-major`.
3. Revise a seção promovida no changelog e rode `make release-dry-run`.
4. Faça merge na `main`.
5. O workflow `release.yml` lê a versão do `pyproject.toml`, cria a tag
   anotada `v<versão>`, extrai a seção correspondente e publica o GitHub
   Release com a wheel anexada.

O workflow é idempotente: se a tag já existir, termina com sucesso sem recriar
tag ou release. O deploy Databricks recebe a versão explicitamente:

```bash
databricks bundle deploy -t prd --var versao="$(python -c 'import tomllib; print(tomllib.load(open("pyproject.toml","rb"))["project"]["version"])')"
```

Jobs Databricks recebem a tag `versao`, e cada registro de linhagem contém
`versao_pacote` e `git_sha`. Assim é possível identificar a versão em execução
por branch, merge ou job publicado.
