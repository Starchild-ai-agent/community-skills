---
name: "@6171/doc-to-markdown"
version: 1.0.0
description: |
  Universal document-to-Markdown converter. Convert PDF, Word (.docx), PowerPoint
  (.pptx), Excel (.xlsx/.csv), HTML, and plain text files into clean, LLM-friendly
  Markdown. Extracts text, tables, images references, and structure (headings,
  lists, slides) with proper formatting preservation.

  Use when the user asks to convert a document to Markdown, extract text from a
  PDF/Word/PPT/Excel file, or make document content readable for AI processing.
author: starchild
tags: [document, converter, markdown, pdf, docx, pptx, xlsx, extraction]
delivery: script
metadata:
  starchild:
    emoji: "📄"
    skillKey: doc-to-markdown
---

# 📄 doc-to-markdown

Universal document-to-Markdown converter. Turn PDF, Word, PowerPoint, Excel,
HTML, and text files into clean Markdown — preserving headings, tables, lists,
and structure. Designed for AI agents that need to read document content.

## Supported formats

| Format | Extensions | Library | Notes |
|---|---|---|---|
| PDF | `.pdf` | `pdfplumber` | Text + tables extracted page by page |
| Word | `.docx` | `python-docx` | Headings, paragraphs, tables, lists |
| PowerPoint | `.pptx` | `python-pptx` | Slide-by-slide, titles + body text + tables |
| Excel | `.xlsx` | `openpyxl` | Each sheet → Markdown table |
| CSV | `.csv` | stdlib `csv` | First row = header row |
| HTML | `.html`, `.htm` | `BeautifulSoup` | Strips tags, keeps structure |
| Text | `.txt`, `.md`, `.rst` | stdlib | Pass-through with light cleanup |

## How to call

```bash
python3 skills/doc-to-markdown/convert.py <input_file> [--output <output_file>] [--format json]
```

- `--output`: write Markdown to a file instead of stdout
- `--format json`: return `{"success": true, "markdown": "...", "format": "...", "pages": N, "tables": N}` as JSON

### Example — convert a PDF

```bash
python3 skills/doc-to-markdown/convert.py report.pdf --output report.md
```

### Example — convert and get JSON

```bash
python3 skills/doc-to-markdown/convert.py slides.pptx --format json
```

### Example — convert Word doc inline

```bash
MD=$(python3 skills/doc-to-markdown/convert.py document.docx)
echo "$MD"
```

## Output structure

The converter produces clean Markdown with:

- **PDF**: Each page separated by `---`, tables rendered as Markdown tables
- **Word**: Headings mapped to `#`/`##`/`###`, tables as Markdown tables, lists preserved
- **PowerPoint**: Each slide as `## Slide N: <title>`, body text as bullet points
- **Excel**: Each sheet as `## Sheet: <name>`, data as Markdown table
- **HTML**: Semantic tags converted (h1-h6, ul/ol, table, p, code, blockquote)

## Dependencies

All dependencies are pre-installed in the Starchild environment:
- `pdfplumber` — PDF text and table extraction
- `python-docx` — Word document parsing
- `python-pptx` — PowerPoint parsing
- `openpyxl` — Excel spreadsheet reading
- `beautifulsoup4` — HTML parsing

No API keys required. All conversion runs locally.

## Error handling

- Unsupported file extension → returns error with supported formats list
- Corrupted/unreadable file → returns error with details
- Empty file → returns empty Markdown with success=true

## Use cases

- Feed document content to an LLM for summarization or Q&A
- Extract structured data from reports for analysis
- Convert legacy documents for migration
- Make attachments readable in agent workflows
- Preprocess files for RAG pipelines
