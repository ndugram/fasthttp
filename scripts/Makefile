.PHONY: lint clean dev dev-release build format

lint:
	ruff check .
	mypy fasthttp


clean:
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
	rm -rf .mypy_cache
	rm -rf .ruff_cache


dev:
	python -m maturin develop


dev-release:
	python -m maturin develop --release


build:
	python -m maturin build --release --out dist


format:
	ruff format .
