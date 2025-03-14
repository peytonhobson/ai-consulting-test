.PHONY: install install-dev format lint test clean test_llm

install-dev:
	pip install -r requirements-dev.txt

install: download-model-files
	pip install -e .
	pip install -r requirements.txt

download-model-files:
	python src/utils/download_model_files.py

format:
	black .
	isort .

lint:
	flake8 .
	mypy .

test_llm:
	streamlit run test_llm.py
	
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
