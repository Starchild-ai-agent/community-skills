---
name: "@6171/pdf-toolkit"
version: 1.0.0
description: |
  Inspect, extract text, merge, split, and classify PDFs. Use when the user wants to work with PDF documents — extract text, check metadata, merge/split pages, or classify scanned vs digital PDFs.
metadata:
  starchild:
    emoji: "📄"
    skillKey: pdf-toolkit
    requires:
      bins: [python3]
    install:
      - kind: pip
        package: pypdf
      - kind: pip
        package: pdfplumber
user-invocable: true
---

# PDF Toolkit

## Core Capabilities

| Action | Description | Command |
|--------|-------------|---------|
| **Info** | Extract metadata (title, author, pages, size, PDF version) | `--action info --input file.pdf` |
| **Text** | Extract all text from every page | `--action text --input file.pdf` |
| **Classify** | Detect scanned (image-based) vs text-based PDF | `--action classify --input file.pdf` |
| **Merge** | Combine multiple PDFs into one | `--action merge --inputs a.pdf b.pdf --output merged.pdf` |
| **Split** | Split into individual pages | `--action split --input file.pdf --output-dir out/` |

## Usage

```bash
# Quick info
python3 skills/pdf-toolkit/scripts/pdf_extract.py --action info --input report.pdf

# Extract text
python3 skills/pdf-toolkit/scripts/pdf_extract.py --action text --input report.pdf --json

# Check if scanned
python3 skills/pdf-toolkit/scripts/pdf_extract.py --action classify --input report.pdf

# Merge
python3 skills/pdf-toolkit/scripts/pdf_extract.py --action merge --inputs a.pdf b.pdf --output combined.pdf

# Split into pages
python3 skills/pdf-toolkit/scripts/pdf_extract.py --action split --input report.pdf --output-dir output/pages
```

## Gotchas

- **Scanned PDFs** (no selectable text) produce empty text extraction. The `classify` action detects this. For OCR, recommend an external OCR tool (Tesseract, etc.).
- **Encrypted PDFs** need `--password`. pypdf handles most encryption types.
- **Large PDFs** (1000+ pages) — `text` extraction with pdfplumber is slower but higher quality than pypdf. Use `info` first to check page count.
- **Merge** preserves all pages from each input file.
- **Split** outputs to `--output-dir` (default: `output/split_pages`), each page named `page_0001.pdf`.