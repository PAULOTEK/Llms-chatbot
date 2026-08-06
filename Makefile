.PHONY: install lint format test
install:
	python -m pip install -e '.[dev]'
lint:
	ruff check .
format:
	black .
test:
	pytest -q
