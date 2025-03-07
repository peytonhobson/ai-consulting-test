.PHONY: install format lint test clean test_llm

install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

format:
	black .
	isort .

lint:
	flake8 .
	mypy .

test:
	pytest

# Add server run command
test_llm:
	python ./src/scripts/test_llm.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
