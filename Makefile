# PSMonitor Makefile

VENV := .venv
UPX_VER := 5.0.1
BUILD_SCRIPT := build.py

ifeq ($(OS),Windows_NT)
    PYTHON := $(VENV)/Scripts/python.exe
    PIP := $(VENV)/Scripts/pip.exe
else
    PYTHON := $(VENV)/bin/python
    PIP := $(VENV)/bin/pip
endif

.PHONY: all
all: help

.PHONY: help
help:
	@echo PSMonitor Makefile
	@echo
	@echo Available targets:
	@echo   venv             Create virtual environment
	@echo   install          Install Python dependencies
	@echo   build-gui        Build GUI executable
	@echo   build-headless   Build headless executable

.PHONY: venv
venv:
	python -m venv $(VENV)

.PHONY: install
install: venv
	$(PIP) install -r requirements.txt

.PHONY: build-gui
build-gui: install
	$(PYTHON) $(BUILD_SCRIPT) --build gui --upx $(UPX_VER) --clean

.PHONY: build-headless
build-headless: install
	$(PYTHON) $(BUILD_SCRIPT) --build headless --upx $(UPX_VER) --clean