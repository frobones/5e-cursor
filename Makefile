# D&D Reference Extraction Makefile

.PHONY: all submodule extract clean help install deps venv
.PHONY: campaign-init import-character encounter rules session add-npc add-location test

# Detect venv python
PYTHON := $(shell [ -f .venv/bin/python ] && echo ".venv/bin/python" || echo "python3")

# Default target: install deps, ensure submodule is ready, then extract
all: install submodule extract
	@echo ""
	@echo "Ready to go! D&D reference data is available in books."

# Create virtual environment and install requirements
install: venv
	@echo "Installing Python requirements..."
	@.venv/bin/pip install -q -r requirements.txt
	@echo "Requirements installed."

# Alias for install
deps: install

# Create virtual environment if it doesn't exist
venv:
	@if [ ! -d .venv ]; then \
		echo "Creating virtual environment..."; \
		python3 -m venv .venv; \
		echo "Virtual environment created."; \
	fi

# Initialize/update the 5etools-src submodule
submodule:
	@echo "Initializing 5etools-src submodule..."
	git submodule update --init --recursive
	@echo "Submodule ready."

# Run the extraction script
# Usage: make extract
# Or: make extract SOURCES="XPHB,XDMG"
extract:
	@echo "Extracting D&D reference data..."
ifdef SOURCES
	@DND_SOURCES="$(SOURCES)" $(PYTHON) scripts/extract_all.py
else
	@$(PYTHON) scripts/extract_all.py
endif
	@echo "Extraction complete. See books/ directory."

# Clean extracted data (can be regenerated)
clean:
	@echo "Removing extracted books/ content..."
	rm -rf books/
	@echo "Clean complete. Run 'make extract' to regenerate."

# ==================== Campaign Assistant ====================

# Initialize a new campaign
# Usage: make campaign-init NAME="My Campaign"
campaign-init:
	@$(PYTHON) scripts/campaign/init_campaign.py "$(or $(NAME),My Campaign)"

# Import a character from D&D Beyond
# Usage: make import-character URL="https://www.dndbeyond.com/characters/12345"
import-character:
ifndef URL
	$(error URL is required. Usage: make import-character URL="https://www.dndbeyond.com/characters/12345")
endif
	@$(PYTHON) scripts/campaign/import_character.py "$(URL)"

# Build an encounter
# Usage: make encounter LEVEL=3 SIZE=4 DIFFICULTY=medium
# Or: make encounter AUTO=1 DIFFICULTY=hard
encounter:
ifdef AUTO
	@$(PYTHON) scripts/campaign/encounter_builder.py --auto --difficulty $(or $(DIFFICULTY),medium)
else
	@$(PYTHON) scripts/campaign/encounter_builder.py --level $(or $(LEVEL),1) --size $(or $(SIZE),4) --difficulty $(or $(DIFFICULTY),medium)
endif

# Look up a rule
# Usage: make rules QUERY="fireball"
# Or: make rules SPELL="magic missile"
rules:
ifdef SPELL
	@$(PYTHON) scripts/campaign/rules_engine.py --spell "$(SPELL)"
else ifdef CREATURE
	@$(PYTHON) scripts/campaign/rules_engine.py --creature "$(CREATURE)"
else ifdef FEAT
	@$(PYTHON) scripts/campaign/rules_engine.py --feat "$(FEAT)"
else
	@$(PYTHON) scripts/campaign/rules_engine.py "$(or $(QUERY),help)"
endif

# Create a new session
# Usage: make session TITLE="The Beginning"
session:
	@$(PYTHON) scripts/campaign/session_manager.py new "$(or $(TITLE),Untitled Session)"

# List sessions
sessions:
	@$(PYTHON) scripts/campaign/session_manager.py list

# Add an NPC
# Usage: make add-npc NAME="Elara" ROLE=ally
add-npc:
ifndef NAME
	$(error NAME is required. Usage: make add-npc NAME="NPC Name" ROLE=ally)
endif
	@$(PYTHON) scripts/campaign/campaign_manager.py add-npc "$(NAME)" --role $(or $(ROLE),neutral)

# Add a location
# Usage: make add-location NAME="The Tavern" TYPE=tavern
add-location:
ifndef NAME
	$(error NAME is required. Usage: make add-location NAME="Location Name" TYPE=tavern)
endif
	@$(PYTHON) scripts/campaign/campaign_manager.py add-location "$(NAME)" --type $(or $(TYPE),other)

# List NPCs
npcs:
	@$(PYTHON) scripts/campaign/campaign_manager.py list-npcs

# List locations
locations:
	@$(PYTHON) scripts/campaign/campaign_manager.py list-locations

# Run tests
test:
	@$(PYTHON) -m pytest tests/ -v

# ==================== Help ====================

# Show help
help:
	@echo "D&D Reference Extraction & Campaign Assistant"
	@echo ""
	@echo "Setup Commands:"
	@echo "  make              - Full setup: install deps, init submodule, extract (default)"
	@echo "  make install      - Create venv and install Python requirements"
	@echo "  make submodule    - Initialize/update 5etools-src submodule only"
	@echo "  make extract      - Run extraction (uses sources.yaml or defaults)"
	@echo "  make extract SOURCES=\"XPHB,XMM\"  - Extract specific sources only"
	@echo "  make clean        - Remove extracted books/ directory"
	@echo ""
	@echo "Campaign Commands:"
	@echo "  make campaign-init NAME=\"My Campaign\"  - Initialize a new campaign"
	@echo "  make import-character URL=\"...\"        - Import D&D Beyond character"
	@echo "  make encounter LEVEL=3 SIZE=4 DIFFICULTY=medium"
	@echo "  make encounter AUTO=1 DIFFICULTY=hard   - Auto-detect party"
	@echo "  make rules QUERY=\"prone condition\"     - Look up a rule"
	@echo "  make rules SPELL=\"fireball\"            - Look up a spell"
	@echo "  make session TITLE=\"Session Name\"      - Create new session"
	@echo "  make sessions                          - List all sessions"
	@echo "  make add-npc NAME=\"NPC\" ROLE=ally      - Add an NPC"
	@echo "  make add-location NAME=\"Place\" TYPE=tavern"
	@echo "  make npcs                              - List all NPCs"
	@echo "  make locations                         - List all locations"
	@echo "  make test                              - Run tests"
	@echo ""
	@echo "  make help         - Show this help message"
