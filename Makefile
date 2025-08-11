# this target will be executed by default
# it will generate a list of all targets in this Makefile
.DEFAULT_GOAL := help
.PHONY: help, fmt, test, test_all, gui
help:			## Show this help.
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep "^[a-zA-Z0-9_-]*:" Makefile

# when adding new targets, make sure to add a description with ##
# and put a tab before the comment for formatting purposes

init:
	@if ! command -v uv &> /dev/null; then \
		echo "❌ UV is not installed. Please install it first."; \
		echo "see: https://docs.astral.sh/uv/getting-started/installation/"; \
		exit 1; \
	fi
	
	uv sync

	mv scripts/pre-commit .git/hooks/pre-commit
	mv scripts/pre-push .git/hooks/pre-push

	@echo "🎉 Environment setup complete!"
	@echo ""
	@echo "📋 Next steps:"
	@echo "1. Copy sample.env to .env and add your API credentials:"
	@echo "   cp sample.env .env"
	@echo "   # Then edit .env with your API_BASE_URL and API_AUTH_KEY"
	@echo ""
	@echo "2. To activate the environment and start Jupyter:"
	@echo "   uv run jupyter lab"
	@echo ""
	@echo "   Or to run the notebook directly:"
	@echo "   uv run jupyter notebook notebook-examples/0_quickstart.ipynb"
	@echo ""
	@echo "   Or to activate the shell environment:"
	@echo "   source .venv/bin/activate"



fmt:			## Auto-format code.
	uv run ruff check --fix .
	uv run ruff format .


