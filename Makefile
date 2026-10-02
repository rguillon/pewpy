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

.PHONY: dev
dev: ## Run the game with the dev screens: models, bosses, candidates, AI learning and rating (src/pewpewdev)
	@if [ -e /dev/dxg ]; then GALLIUM_DRIVER=d3d12 uv run python -m pewpewdev; else uv run python -m pewpewdev; fi

.PHONY: candidates
candidates: ## Generate enemy model candidates for the Enemy candidates screen (options: ARGS="--kind aircraft --count 50", see --help)
	@uv run python -m pewpewdev.tools.make_candidates $(ARGS)

.PHONY: boss-candidates
boss-candidates: ## Generate boss model candidates for the Boss candidates screen (options: ARGS="--count 20", see --help)
	@uv run python -m pewpewdev.tools.make_boss_candidates $(ARGS)

.PHONY: levels
levels: ## Generate the game's levels from the worlds' plan in src/pewpewdev/tools/make_levels.py (options: ARGS="--seed 1234", see --help)
	@uv run python -m pewpewdev.tools.make_levels $(ARGS)

.PHONY: final-bosses
final-bosses: ## Make the final bosses (data/bosses/final_bosses.json) from their plans in src/pewpewdev/tools/final_boss_plans.json
	@uv run python -m pewpewdev.tools.make_final_bosses $(ARGS)

.PHONY: learn
learn: ## Teach the AI to play, every ship on every level, without a window (options: ARGS="--generations 300 --ships vanguard", see --help)
	@uv run python -u -m pewpewdev.ai learn $(ARGS)

.PHONY: rate
rate: ## Rate every level for every ship from how the trained AI fares: its clear rate (options: ARGS="--runs 20", see --help)
	@uv run python -u -m pewpewdev.ai rate $(ARGS)

.PHONY: songs
songs: ## Generate the game's synthwave songs as MIDI files (options: ARGS="--seed 1234", "--only boss", "--wav", see --help)
	@uv run python -m pewpewdev.tools.make_songs $(ARGS)

.PHONY: models
models: ## Remodel ships in real 3D from their recipes in src/pewpewdev/tools/make_models.py (ARGS="player drone": just these)
	@uv run python -m pewpewdev.tools.make_models $(ARGS)

.PHONY: voxels
voxels: ## Move a model between flat, 3D (layered) and MagicaVoxel forms (ARGS="export drone", "use drone", "layers drone")
	@uv run python -m pewpewdev.tools.voxels $(ARGS)

.PHONY: test
test: ## Test the code with pytest
	@echo "🚀 Testing code: Running pytest"
	@uv run python -m pytest --cov --cov-config=pyproject.toml --cov-report=xml

.PHONY: build
build: clean-build ## Build wheel file
	@echo "🚀 Creating wheel file"
	@uvx --from build pyproject-build --installer uv

.PHONY: package
package: ## Build the standalone Windows game: dist/pewpy-<version>_win_amd64.zip (pewpy.exe inside)
	@echo "🚀 Building the Windows executable with Panda3D's build_apps"
	@uv run python -c "import os; os.makedirs('build', exist_ok=True)"
	@uv export --frozen --no-dev --no-hashes --no-emit-project --quiet -o build/requirements.txt
	@uv run python packaging/setup.py bdist_apps

.PHONY: clean-build
clean-build: ## Clean build artifacts
	@echo "🚀 Removing build artifacts"
	@uv run python -c "import shutil; import os; shutil.rmtree('dist') if os.path.exists('dist') else None"

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
