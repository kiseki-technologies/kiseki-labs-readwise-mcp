SHELL=bash
UV := uv
SRC_DIR := ./
TEST_DIR := tests
PYLINT_THRESHOLD := 6

# Default target
.DEFAULT_GOAL := help

.PHONY: help
help:
	@echo "Available targets:"
	@echo "  lint       		- Run linter on Python files"
	@echo "  lint-ci    		- Run linter and fail if score is below $(PYLINT_THRESHOLD)"
	@echo "  fmt        		- Format Python files using Black"
	@echo "  install    		- Install project dependencies using uv"
	@echo "  install-ci 		- Install project dependencies using uv in a CI environment"
	@echo "  test       		- Run tests using pytest"

.PHONY: lint
lint:
	$(UV) run pylint $(SRC_DIR) $(TEST_DIR)

.PHONY: lint-ci
lint-ci:
	$(UV) run pylint --fail-under=$(PYLINT_THRESHOLD) $(shell find $(SRC_DIR) -name "*.py")
	$(UV) run pylint --fail-under=$(PYLINT_THRESHOLD) $(shell find $(TEST_DIR) -name "*.py")

.PHONY: fmt
fmt:
	$(UV) run isort $(SRC_DIR) $(TEST_DIR)
	$(UV) run black $(SRC_DIR) $(TEST_DIR)

.PHONY: install
install:
	$(UV) pip install

.PHONY: install-ci
install-ci:
	$(UV) sync --all-extras --dev

.PHONY: test
test:
	$(UV) run pytest
