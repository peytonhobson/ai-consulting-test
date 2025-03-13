.PHONY: install install-dev format lint test clean test_llm

# Detect operating system
ifeq ($(OS),Windows_NT)
    CLEAN_CMD = powershell -ExecutionPolicy Bypass -NoProfile -Command "& { \
        Get-ChildItem -Path . -Directory -Recurse -Filter '__pycache__' | Remove-Item -Recurse -Force; \
        Get-ChildItem -Path . -File -Recurse -Include '*.pyc','*.pyo','*.pyd' | Remove-Item -Force; \
        Get-ChildItem -Path . -Directory -Recurse -Filter '*.egg-info' | Remove-Item -Recurse -Force; \
        Get-ChildItem -Path . -Directory -Recurse -Filter '*.egg' | Remove-Item -Recurse -Force; \
        Get-ChildItem -Path . -Directory -Recurse -Filter '.pytest_cache' | Remove-Item -Recurse -Force; \
        Get-ChildItem -Path . -Directory -Recurse -Filter '.mypy_cache' | Remove-Item -Recurse -Force; \
    }"
else
    CLEAN_CMD = find . -type d -name "__pycache__" -exec rm -rf {} + && \
        find . -type f -name "*.pyc" -delete && \
        find . -type f -name "*.pyo" -delete && \
        find . -type f -name "*.pyd" -delete && \
        find . -type d -name "*.egg-info" -exec rm -rf {} + && \
        find . -type d -name "*.egg" -exec rm -rf {} + && \
        find . -type d -name ".pytest_cache" -exec rm -rf {} + && \
        find . -type d -name ".mypy_cache" -exec rm -rf {} +
endif

install-dev:
	pip install -r requirements-dev.txt

install:
	pip install -e .
	pip install -r requirements.txt

format:
	black .
	isort .

lint:
	flake8 .
	mypy .

test_llm:
	streamlit run test_llm.py
    
clean:
	$(CLEAN_CMD)
