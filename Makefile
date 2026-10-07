.PHONY: install
install: ## Install the virtual environment and install the pre-commit hooks
	@echo "🚀 Creating virtual environment using uv"
	@uv sync
	@uv run pre-commit install

.PHONY: check
check: ## Run code quality tools.
	@echo "🚀 Checking lock file consistency with 'pyproject.toml'"
	@uv lock --locked
	@echo "🚀 Linting code: Running pre-commit"
	@uv run pre-commit run -a
	@echo "🚀 Static type checking: Running ty"
	@uv run ty check
	@echo "🚀 Checking for obsolete dependencies: Running deptry"
	@uv run deptry src

.PHONY: run
run: ## Run the game (under WSL, on the GPU through Mesa's d3d12 driver rather than the much slower CPU renderer)
	@if [ -e /dev/dxg ]; then GALLIUM_DRIVER=d3d12 uv run python -m pewpy; else uv run python -m pewpy; fi

.PHONY: levels
levels: ## Generate the game's levels from the worlds' plans in src/pewpy/generators/levels/worlds/ (options: ARGS="--seed 1234", see --help)
	@uv run python -m pewpy.generators.levels $(ARGS)

.PHONY: learn
learn: ## Teach the AI to play, every ship on every level, without a window (options: ARGS="--generations 300 --ships vanguard", see --help)
	@uv run python -u -m pewpy.generators.ai_training learn $(ARGS)

.PHONY: learn-level1
learn-level1: ## Teach the AI to play level 1-1 only, every ship (options: ARGS="--generations 300 --new", see --help)
	@uv run python -u -m pewpy.generators.ai_training learn --levels 1-1 $(ARGS)

.PHONY: learn-random
learn-random: ## Teach the AI on levels drawn at random among them all, no curriculum (options: ARGS="--generations 300")
	@uv run python -u -m pewpy.generators.ai_training learn --levels all $(ARGS)

.PHONY: winrate
winrate: ## Play every level with the current brain and show its win rates, saving nothing (options: ARGS="--runs 20 --lives 3")
	@uv run python -u -m pewpy.generators.ai_training winrate $(ARGS)

.PHONY: test
test: ## Test the code with pytest
	@echo "🚀 Testing code: Running pytest"
	@uv run python -m pytest --cov --cov-config=pyproject.toml --cov-report=xml

.PHONY: mutate
mutate: ## Test the tests: mutate the code with mutmut and report the mutants the tests let survive (options: ARGS="pewpy.game.score*")
	@echo "🚀 Testing the tests: Running mutmut"
	@uv run mutmut run $(ARGS) && uv run mutmut results

.PHONY: docs-test
docs-test: ## Test if documentation can be built without warnings or errors
	@uv run mkdocs build -s

.PHONY: docs
docs: ## Build and serve the documentation
	@uv run mkdocs serve

.PHONY: help
help:
	@uv run python -c "import re; \
	[[print(f'\033[36m{m[0]:<20}\033[0m {m[1]}') for m in re.findall(r'^([a-zA-Z_-]+):.*?## (.*)$$', open(makefile).read(), re.M)] for makefile in ('$(MAKEFILE_LIST)').strip().split()]"

.DEFAULT_GOAL := help
