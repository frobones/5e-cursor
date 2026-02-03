# 5e-cursor — D&D campaign assistant
# Run: make help

PYTHON := $(shell [ -f .venv/bin/python ] && echo ".venv/bin/python" || echo "python3")

# ---- Setup ----

.PHONY: all install extract clean campaign-init demo-campaign demo-campaign-clean frontend-install web-ui web-ui-stop help

all: install submodule extract
	@echo ""
	@echo "Ready. Reference data is in books/."

install: venv
	@echo "Installing Python requirements..."
	@.venv/bin/pip install -q -r requirements.txt
	@echo "Done."

venv:
	@if [ ! -d .venv ]; then python3 -m venv .venv; echo "Venv created."; fi

submodule:
	@git submodule update --init --recursive
	@echo "Submodule ready."

extract:
	@echo "Extracting reference data..."
ifdef SOURCES
	@DND_SOURCES="$(SOURCES)" $(PYTHON) scripts/extract_all.py
else
	@$(PYTHON) scripts/extract_all.py
endif
	@echo "Done. See books/."

clean:
	@rm -rf books/
	@echo "Cleaned. Run make extract to regenerate."

# ---- Campaign ----

campaign-init:
	@$(PYTHON) scripts/campaign/init_campaign.py "$(or $(NAME),My Campaign)"

# ---- Demo Campaign ----

demo-campaign:
	@if [ -d campaign ]; then \
		echo "Error: campaign/ already exists. Run 'make demo-campaign-clean' first."; \
		exit 1; \
	fi
	@echo "Extracting demo campaign..."
	@unzip -q demo-campaign.zip
	@touch campaign/.demo
	@echo "Demo campaign ready. Run 'make web-ui' to explore."

demo-campaign-clean:
	@if [ -f campaign/.demo ]; then \
		rm -rf campaign/; \
		echo "Demo campaign removed."; \
	elif [ -d campaign ]; then \
		echo "Error: campaign/ exists but is not the demo campaign."; \
		echo "Use 'rm -rf campaign/' manually if you really want to delete it."; \
		exit 1; \
	else \
		echo "No demo campaign found."; \
	fi

# ---- Web UI ----

frontend-install:
	@if [ ! -d frontend/node_modules ]; then \
		echo "Installing frontend dependencies..."; \
		cd frontend && npm install; \
	fi

web-ui: frontend-install
	@rm -f .web-ui.pids
	@mkdir -p logs
	@PYTHONPATH=scripts $(PYTHON) -m web.main >> logs/backend.log 2>&1 & \
	echo $$! >> .web-ui.pids; \
	(cd frontend && exec npm run dev >> ../logs/frontend.log 2>&1) & \
	echo $$! >> .web-ui.pids; \
	echo ""; \
	echo "Web UI started."; \
	echo "  Frontend: http://localhost:5173"; \
	echo "  Backend:  http://localhost:8000"; \
	echo ""; \
	echo "Logs:"; \
	echo "  Backend:  logs/web-ui.log"; \
	echo "  Frontend: logs/frontend.log"; \
	echo ""; \
	echo "Stop with: make web-ui-stop"; \
	sleep 3

web-ui-stop:
	@if [ -f .web-ui.pids ]; then \
		while read pid; do kill $$pid 2>/dev/null || true; done < .web-ui.pids; \
		rm -f .web-ui.pids; \
		echo "Web UI stopped."; \
	else \
		echo "No Web UI processes found (run make web-ui first)."; \
	fi

# ---- Help ----

help:
	@echo "5e-cursor — D&D campaign assistant"
	@echo ""
	@echo "Setup"
	@echo "  make              Full setup (venv, submodule, extract)"
	@echo "  make extract      Extract reference data (optional: SOURCES=XPHB,XDMG)"
	@echo "  make clean        Remove books/"
	@echo ""
	@echo "Campaign"
	@echo "  make campaign-init NAME=\"My Campaign\""
	@echo ""
	@echo "Demo Campaign"
	@echo "  make demo-campaign        Extract demo campaign for Web UI"
	@echo "  make demo-campaign-clean  Remove demo campaign"
	@echo ""
	@echo "Web UI"
	@echo "  make web-ui       Start app → http://localhost:5173"
	@echo "  make web-ui-stop  Stop app"
	@echo ""
	@echo "More: docs/00-guide.md and docs/08-cli-reference.md"
