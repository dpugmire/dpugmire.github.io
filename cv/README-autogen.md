# Auto-Generated CV System

This directory contains a complete system for auto-generating your academic CV from your website data.

## 🎯 Overview

Your CV is automatically generated from the same data that powers your website:
- **Professional Experience** & **Education** from `data/about.md`
- **Awards** from `data/awards.yaml` plus `Best Paper Award` notes in `data/publications.yaml`
- **Publications** from `data/publications.yaml`
- **Talks** from `data/talks.yaml`
- **Keynotes** from `data/keynotes.yaml`
- **Tutorials** from `data/tutorials.yaml`

**Key Benefit**: Update your website data once, and your CV updates automatically. No more maintaining two separate documents!

## 🚀 Quick Start

### Generate your CV:
```bash
cd cv
make
```

That's it! Your CV is now at `cv/output/PugmireCV.pdf`

## 📁 Directory Structure

```
cv/
├── generate_cv.py              # Main generator script
├── Makefile                    # Easy build commands
├── templates/
│   └── cv_template.tex         # LaTeX template (customize this!)
├── output/                     # Output directory (auto-created)
│   ├── cv.tex                  # Generated LaTeX
│   └── PugmireCV.pdf           # Compiled PDF
└── README-autogen.md           # This file
```

## 🛠️ Usage

### Generate and compile CV:
```bash
make
```

### Just generate LaTeX (no compilation):
```bash
make gen
```

### Just compile existing LaTeX:
```bash
make pdf
```

### Clean auxiliary files:
```bash
make clean
```

### View all commands:
```bash
make help
```

## 🔧 How It Works

1. **`generate_cv.py`** reads your website data files
2. Parses markdown tables and YAML files
3. Populates the LaTeX template with your data
4. Outputs `output/cv.tex`
5. **`make pdf`** compiles the LaTeX to PDF using `pdflatex`

## ✏️ Customization

### Modify CV Template

Edit `templates/cv_template.tex` to customize:
- Header formatting
- Section layout
- Font sizes and styles
- Colors
- Spacing

The template uses placeholders that are automatically filled:
- `{{PROFESSIONAL_EXPERIENCE}}` - Your work history
- `{{EDUCATION}}` - Your degrees
- `{{PUBLICATIONS}}` - Auto-formatted publication list
- `{{PRESENTATIONS}}` - Talks, keynotes, tutorials
- `{{GENERATION_DATE}}` - When CV was generated

### Modify Generator Logic

Edit `generate_cv.py` to change:
- Publication formatting
- Section ordering
- Filtering (e.g., only show last 5 years of talks)
- Custom sections

## 📊 Data Sources

The generator reads from these files in your website's `data/` directory:

| File | Contents | Format |
|------|----------|--------|
| `about.md` | Professional Experience, Education | Markdown tables |
| `publications.yaml` | All publications | YAML with structured metadata |
| `talks.yaml` | Invited talks | YAML with title, venue, location, date |
| `keynotes.yaml` | Keynote presentations | YAML |
| `tutorials.yaml` | Tutorial presentations | YAML |

## 🔄 Workflow

**Typical workflow:**

1. Update your website data (e.g., add a new publication to `publications.yaml`)
2. Run `make` in the `cv/` directory
3. Your CV is automatically updated with the new publication
4. Share `output/PugmireCV.pdf`

**No manual editing of LaTeX needed!**

## 📋 What Gets Generated

### Current Sections:
- ✅ Professional Experience (from about.md)
- ✅ Education (from about.md)
- ✅ Publications (grouped by type: Journal, Conference, Workshop, etc.)
- ✅ Presentations (Keynotes, Tutorials, Invited Talks)
- ⚠️  Professional Service (partially hardcoded - needs data source)
- ⚠️  Awards (partially hardcoded - needs data source)

### To Add More Sections:

1. Create a YAML file in `data/` (e.g., `data/awards.yaml`)
2. Add parsing logic in `generate_cv.py`
3. Add placeholder in `templates/cv_template.tex`
4. Update generator to fill the placeholder

## 🐛 Troubleshooting

### "pdflatex: command not found"

Install LaTeX:
- **macOS**: `brew install --cask mactex`
- **Ubuntu**: `sudo apt-get install texlive-full`
- **Fedora**: `sudo dnf install texlive-scheme-full`

### "ModuleNotFoundError: No module named 'yaml'"

Install PyYAML:
```bash
pip install pyyaml
```

Or use the Makefile:
```bash
make install-deps
```

### LaTeX Compilation Errors

Check the log:
```bash
cat output/cv.log
```

Common issues:
- Special characters not escaped (the generator should handle this)
- Missing LaTeX packages (install texlive-full)

### CV looks wrong

1. Check the generated LaTeX: `output/cv.tex`
2. Modify the template: `templates/cv_template.tex`
3. Adjust generator logic: `generate_cv.py`

## 🎨 Styling Tips

The current template is clean and professional. To customize:

### Use a different LaTeX CV class:

Replace the template with `moderncv`, `awesome-cv`, or another CV class:
1. Find a CV template you like
2. Save it as `templates/cv_template.tex`
3. Add the same placeholders (`{{PROFESSIONAL_EXPERIENCE}}`, etc.)
4. Run `make`

### Adjust margins:

In `templates/cv_template.tex`, change:
```latex
\usepackage[margin=0.75in]{geometry}
```

### Change colors:

```latex
\definecolor{primary}{RGB}{0, 102, 204}
\hypersetup{urlcolor=primary}
```

### Different font:

```latex
\usepackage{mathptmx}  % Times Roman
% or
\usepackage{helvet}    % Helvetica
```

## 📈 Future Enhancements

Possible additions:
- [ ] Parse `professional_activities.yaml` for service roles
- [ ] Add awards from a YAML file
- [ ] Generate both full CV and short 2-page resume
- [ ] Multiple CV formats (academic, industry, government)
- [ ] Auto-highlight your name in publication author lists
- [ ] Add citation counts from Google Scholar
- [ ] Generate HTML version alongside PDF

## 🤝 Contributing

To improve the CV generator:

1. Edit the generator script: `generate_cv.py`
2. Test: `make`
3. Update this README if you add features

## 📝 Notes

- The generator preserves all your original data files unchanged
- Generated files go to `output/` directory
- It's safe to delete `output/` - it will be recreated
- Your old manual `cv.tex` is preserved (not overwritten)
- Run `make` whenever you update website data

## 📞 Support

If you encounter issues:
1. Check this README
2. Run `make help`
3. Check `output/cv.log` for LaTeX errors
4. Review the generated LaTeX at `output/cv.tex`

---

**Last updated**: 2026-02-13
**Version**: 1.0
