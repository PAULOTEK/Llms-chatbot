.PHONY: install lint format test
install:
	python -m pip install -e '.[dev]'
lint:
	ruff check .
format:
	black .
test:
	pytest -q
bump-patch:
	python scripts/bump_versao.py patch
bump-minor:
	python scripts/bump_versao.py minor
bump-major:
	python scripts/bump_versao.py major
changelog:
	python scripts/changelog.py --version "$$(python -c 'import tomllib; print(tomllib.load(open("pyproject.toml","rb"))["project"]["version"])')"
release-dry-run:
	python -m build --wheel
	python scripts/changelog.py --version "$$(python -c 'import tomllib; print(tomllib.load(open("pyproject.toml","rb"))["project"]["version"])')"
