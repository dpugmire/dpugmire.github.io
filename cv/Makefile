# Makefile for auto-generating and compiling CV
# Usage:
#   make        - Generate and compile CV
#   make gen    - Generate CV LaTeX from data
#   make pdf    - Compile LaTeX to PDF
#   make clean  - Remove auxiliary files
#   make help   - Show this help

.PHONY: all gen pdf clean help view

# Default target
all: gen pdf
	@echo ""
	@echo "✅ CV generated and compiled successfully!"
	@echo "📄 Output: generated/cv.pdf"
	@echo ""

# Generate CV from website data
gen:
	@echo "🔄 Generating CV from website data..."
	python3 generate_cv.py

# Compile LaTeX to PDF
pdf:
	@echo "📝 Compiling LaTeX to PDF..."
	@cd generated && pdflatex cv.tex > /dev/null 2>&1 || pdflatex cv.tex
	@cd generated && pdflatex cv.tex > /dev/null 2>&1  # Run twice for references
	@echo "✅ PDF compilation complete"

# View the generated PDF (macOS)
view: all
	@if [ -f generated/cv.pdf ]; then \
		open generated/cv.pdf; \
	else \
		echo "❌ No PDF found. Run 'make' first."; \
	fi

# Clean auxiliary files
clean:
	@echo "🧹 Cleaning auxiliary files..."
	@cd generated && rm -f *.aux *.log *.out *.toc *.bbl *.blg *.bcf *.run.xml
	@echo "✅ Cleaned"

# Deep clean (remove generated files too)
distclean: clean
	@echo "🧹 Deep cleaning (removing generated files)..."
	@rm -rf generated/*
	@echo "✅ All generated files removed"

# Show help
help:
	@echo "CV Auto-Generation Makefile"
	@echo ""
	@echo "Targets:"
	@echo "  make         - Generate CV from data and compile to PDF"
	@echo "  make gen     - Only generate LaTeX from website data"
	@echo "  make pdf     - Only compile LaTeX to PDF"
	@echo "  make view    - Generate, compile, and open PDF (macOS)"
	@echo "  make clean   - Remove auxiliary LaTeX files"
	@echo "  make distclean - Remove all generated files"
	@echo "  make help    - Show this help"
	@echo ""
	@echo "Workflow:"
	@echo "  1. Edit your website data files (data/*.yaml, data/about.md)"
	@echo "  2. Run 'make' to regenerate your CV"
	@echo "  3. Your CV is at: generated/cv.pdf"
	@echo ""

# Install dependencies (for reference)
install-deps:
	@echo "📦 Installing Python dependencies..."
	pip install pyyaml
	@echo "✅ Dependencies installed"
	@echo ""
	@echo "⚠️  You also need LaTeX installed:"
	@echo "  macOS:   brew install --cask mactex"
	@echo "  Ubuntu:  sudo apt-get install texlive-full"
	@echo "  Fedora:  sudo dnf install texlive-scheme-full"
