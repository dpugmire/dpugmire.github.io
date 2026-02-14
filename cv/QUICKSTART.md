# CV Auto-Generator - Quick Start

## ⚡ TL;DR

```bash
cd cv
make
```

Your auto-generated CV is now at: `cv/generated/cv.pdf`

## 📊 What Was Generated

✅ **11-page PDF CV** including:
- Professional Experience (11 positions from your career)
- Education (Ph.D. and B.S. from University of Utah)
- Publications (127 papers: journals, conferences, workshops, etc.)
- Presentations (45 invited talks, recent 5 years)
- Professional Service
- Awards & Honors

## 🎯 Key Features

### Single Source of Truth
All data comes from your website:
- `data/about.md` → Professional Experience & Education
- `data/publications.yaml` → 127 publications, auto-sorted by type and year
- `data/talks.yaml` → 45 talks
- `data/keynotes.yaml` → Keynote presentations
- `data/tutorials.yaml` → Tutorial sessions

### One Command Updates
```bash
# Edit your website data files
vim ../data/publications.yaml

# Regenerate CV
make

# Done! Your CV is updated.
```

## 📁 What's New

```
cv/
├── generate_cv.py           ← Python script that reads website data
├── Makefile                 ← Simple build commands
├── templates/
│   └── cv_template.tex      ← LaTeX template (customize this!)
├── generated/               ← Auto-generated files
│   ├── cv.tex              ← Generated LaTeX
│   └── cv.pdf              ← Your CV (11 pages)
├── README-autogen.md        ← Full documentation
└── QUICKSTART.md            ← This file
```

## 🔧 Common Tasks

### Update your CV:
```bash
# 1. Edit website data
vim ../data/publications.yaml

# 2. Regenerate
cd cv && make
```

### Customize appearance:
```bash
# Edit the LaTeX template
vim templates/cv_template.tex

# Regenerate
make
```

### Just generate LaTeX (no compile):
```bash
make gen
```

### Clean build files:
```bash
make clean
```

## 🎨 Customization

The template (`templates/cv_template.tex`) is easy to customize:

**Change margins:**
```latex
\usepackage[margin=0.75in]{geometry}  % Make it 1in, 0.5in, etc.
```

**Change colors:**
```latex
\hypersetup{urlcolor=red}  % or blue, green, etc.
```

**Reorder sections:**
Just move the section blocks around in the template.

## 🐛 Troubleshooting

**"pdflatex: command not found"**
```bash
# macOS
brew install --cask mactex

# Ubuntu
sudo apt-get install texlive-full
```

**"No module named yaml"**
```bash
pip install pyyaml
```

## 📚 Learn More

- Full documentation: `README-autogen.md`
- See all Make commands: `make help`
- Check generated LaTeX: `generated/cv.tex`

## ✨ What Happens Automatically

When you run `make`:

1. ✅ Parses 11 professional positions from `about.md`
2. ✅ Parses 3 education entries from `about.md`
3. ✅ Loads 127 publications from `publications.yaml`
4. ✅ Sorts publications by type (journal, conference, workshop, etc.)
5. ✅ Formats publications with DOI links
6. ✅ Adds recent talks (last 5 years from 45 total)
7. ✅ Generates complete `cv.tex` file
8. ✅ Compiles to PDF (runs pdflatex twice for references)
9. ✅ Creates 11-page professional CV

**No manual editing required!**

---

**Next Steps:**
1. Run `make` to see your generated CV
2. Open `generated/cv.pdf`
3. Customize `templates/cv_template.tex` if desired
4. Keep your website data updated - your CV updates automatically!
