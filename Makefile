include makefilet-download-ondemand.mk

DEBIAN_UPLOAD_TARGET = silicann
PYPI_UPLOAD_TARGET = silicann

BLACK_TARGETS = urwerk_api_client tests setup.py
BLACK_ARGS = --target-version py35
BLACK_BIN = $(PYTHON_BIN) -m black
COVERAGE_BIN ?= $(PYTHON_BIN) -m coverage

default-target: help

.PHONY: lint-python-black
lint-python-black:
	$(BLACK_BIN) $(BLACK_ARGS) --check $(BLACK_TARGETS)

lint-python: lint-python-black

.PHONY: test-report
test-report:
	$(COVERAGE_BIN) report

.PHONY: test-report-short
test-report-short:
	$(MAKE) test-report | grep TOTAL | grep -oP '(\d+)%$$' | sed 's/^/Code Coverage: /'

.PHONY: style
style:
	$(BLACK_BIN) $(BLACK_ARGS) $(BLACK_TARGETS)
