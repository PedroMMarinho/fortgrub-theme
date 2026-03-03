PYTHON_BIN := $(shell which python3)
MAIN_SCRIPT = scripts/main.py

.PHONY: help setup setup-verbose generate

help:
	@echo "Available commands:"
	@echo "  make setup         - Runs the setup-theme command"
	@echo "  make generate      - Runs the generate-theme command"
	
setup:
	@echo "🎮 Setting up Fortnite GRUB theme"
	sudo -E PYTHONPATH=. $(PYTHON_BIN) $(MAIN_SCRIPT) setup-theme

generate:
	@echo "🎮 Generating Fortnite GRUB theme"
	sudo -E PYTHONPATH=. $(PYTHON_BIN) $(MAIN_SCRIPT) generate-theme
