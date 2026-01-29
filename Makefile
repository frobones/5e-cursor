# D&D Reference Extraction Makefile

.PHONY: all submodule extract clean help

# Default target: ensure submodule is ready, then extract
all: submodule extract
	@echo ""
	@echo "Ready to go! D&D reference data is available in books."

# Initialize/update the 5etools-src submodule
submodule:
	@echo "Initializing 5etools-src submodule..."
	git submodule update --init --recursive
	@echo "Submodule ready."

# Run the extraction script
extract:
	@echo "Extracting D&D reference data..."
	python3 scripts/extract_all.py
	@echo "Extraction complete. See books/ directory."

# Clean extracted data (can be regenerated)
clean:
	@echo "Removing extracted books/ content..."
	rm -rf books/
	@echo "Clean complete. Run 'make extract' to regenerate."

# Show help
help:
	@echo "D&D Reference Extraction"
	@echo ""
	@echo "Usage:"
	@echo "  make           - Initialize submodule (if needed) and extract (default)"
	@echo "  make extract   - Run extraction script only"
	@echo "  make submodule - Initialize/update 5etools-src submodule only"
	@echo "  make clean     - Remove extracted books/ directory"
	@echo "  make help      - Show this help message"
