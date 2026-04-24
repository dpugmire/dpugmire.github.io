# Makefile for auto-generating and compiling CV
# Usage:
#   make        - Generate and compile CV
#   make gen    - Generate CV LaTeX from data
#   make pdf    - Compile LaTeX to PDF
#   make clean  - Remove auxiliary files
#   make help   - Show this help

.PHONY: all validate gen pdf clean help view

PYTHON ?= /usr/bin/python3
PDF_NAME ?= PugmireCV.pdf

# Default target
all: gen pdf
	@echo ""
	@echo "✅ CV generated and compiled successfully!"
	@echo "📄 Output: output/$(PDF_NAME)"
	@echo ""

# Validate website data before generating the CV
validate:
	@echo "🔎 Validating website data..."
	$(PYTHON) ../scripts/validate_site_data.py

# Generate CV from website data
gen: validate
	@echo "🔄 Generating CV from website data..."
	$(PYTHON) generate_cv.py

# Compile LaTeX to PDF
pdf:
	@echo "📝 Compiling LaTeX to PDF..."
	@cd output && pdflatex cv.tex > /dev/null 2>&1 || pdflatex cv.tex
	@cd output && pdflatex cv.tex > /dev/null 2>&1  # Run twice for references
	@mv -f output/cv.pdf output/$(PDF_NAME)
	@cp output/$(PDF_NAME) $(PDF_NAME)
	@echo "✅ PDF compilation complete"

# View the generated PDF (macOS)
view: all
	@if [ -f output/$(PDF_NAME) ]; then \
		open output/$(PDF_NAME); \
	else \
		echo "❌ No PDF found. Run 'make' first."; \
	fi

# Clean auxiliary files
clean:
	@echo "🧹 Cleaning auxiliary files..."
	@cd output && rm -f *.aux *.log *.out *.toc *.bbl *.blg *.bcf *.run.xml
	@echo "✅ Cleaned"

# Deep clean (remove output files too)
distclean: clean
	@echo "🧹 Deep cleaning (removing output files)..."
	@rm -rf output/*
	@echo "✅ All generated files removed"

# Show help
help:
	@echo "CV Auto-Generation Makefile"
	@echo ""
	@echo "Targets:"
	@echo "  make         - Generate CV from data and compile to PDF"
	@echo "  make validate - Validate website data files"
	@echo "  make gen     - Only generate LaTeX from website data"
	@echo "  make pdf     - Only compile LaTeX to PDF"
	@echo "  make view    - Generate, compile, and open PDF (macOS)"
	@echo "  make clean   - Remove auxiliary LaTeX files"
	@echo "  make distclean - Remove all output files"
	@echo "  make help    - Show this help"
	@echo ""
	@echo "Workflow:"
	@echo "  1. Edit your website data files (data/*.yaml, data/about.md)"
	@echo "  2. Run 'make validate' to catch schema issues early"
	@echo "  3. Run 'make' to regenerate your CV"
	@echo "  4. Your website-served CV is at: $(PDF_NAME)"
	@echo ""

# Install dependencies (for reference)
install-deps:
	@echo "📦 Installing Python dependencies..."
	$(PYTHON) -m pip install pyyaml
	@echo "✅ Dependencies installed"
	@echo ""
	@echo "⚠️  You also need LaTeX installed:"
	@echo "  macOS:   brew install --cask mactex"
	@echo "  Ubuntu:  sudo apt-get install texlive-full"
	@echo "  Fedora:  sudo dnf install texlive-scheme-full"
