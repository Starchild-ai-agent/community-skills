#!/usr/bin/env python3
"""PDF Toolkit — inspect, extract, classify, merge, split PDFs."""

import argparse
import json
import os
import sys
from pathlib import Path

import pypdf
import pdfplumber


def cmd_info(path: str):
    """Extract PDF metadata."""
    with open(path, "rb") as f:
        reader = pypdf.PdfReader(f)
        meta = reader.metadata or {}
        info = {
            "file": os.path.basename(path),
            "size_bytes": os.path.getsize(path),
            "pages": len(reader.pages),
            "pdf_version": reader.pdf_header,
            "title": meta.get("/Title", ""),
            "author": meta.get("/Author", ""),
            "subject": meta.get("/Subject", ""),
            "creator": meta.get("/Creator", ""),
            "producer": meta.get("/Producer", ""),
            "encrypted": reader.is_encrypted,
        }
        return info


def cmd_text(path: str, password: str = None):
    """Extract all text from a PDF."""
    pages = []
    with pdfplumber.open(path, password=password or "") as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            pages.append({"page": i + 1, "text": text.strip()})
    return pages


def cmd_classify(path: str, password: str = None):
    """Classify PDF as scanned (image-based) or text-based."""
    with pdfplumber.open(path, password=password or "") as pdf:
        total = len(pdf.pages)
        text_pages = 0
        for page in pdf.pages:
            text = page.extract_text() or ""
            if len(text.strip()) > 20:
                text_pages += 1
    ratio = text_pages / total if total > 0 else 0
    return {
        "file": os.path.basename(path),
        "total_pages": total,
        "pages_with_text": text_pages,
        "text_ratio": round(ratio, 3),
        "classification": "scanned" if ratio < 0.1 else "text-based",
    }


def cmd_merge(inputs: list, output: str):
    """Merge multiple PDFs into one."""
    merger = pypdf.PdfWriter()
    for path in inputs:
        merger.append(path)
    with open(output, "wb") as f:
        merger.write(f)
    merger.close()
    return {"merged": len(inputs), "output": output, "pages": len(pypdf.PdfReader(output).pages)}


def cmd_split(path: str, output_dir: str, password: str = None):
    """Split PDF into individual pages."""
    os.makedirs(output_dir, exist_ok=True)
    with open(path, "rb") as f:
        reader = pypdf.PdfReader(f)
        if password and reader.is_encrypted:
            reader.decrypt(password)
        count = 0
        for i, page in enumerate(reader.pages):
            writer = pypdf.PdfWriter()
            writer.add_page(page)
            out_path = os.path.join(output_dir, f"page_{i+1:04d}.pdf")
            with open(out_path, "wb") as out:
                writer.write(out)
            writer.close()
            count += 1
    return {"pages": count, "output_dir": output_dir}


def main():
    parser = argparse.ArgumentParser(description="PDF Toolkit")
    parser.add_argument("--action", required=True, choices=["info", "text", "classify", "merge", "split"])
    parser.add_argument("--input", help="Input PDF path")
    parser.add_argument("--inputs", nargs="+", help="Multiple input PDFs (for merge)")
    parser.add_argument("--output", help="Output PDF path (for merge)")
    parser.add_argument("--output-dir", help="Output directory (for split)")
    parser.add_argument("--password", default=None, help="PDF password")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    result = None
    try:
        if args.action == "info":
            if not args.input:
                raise ValueError("--input required")
            result = cmd_info(args.input)
        elif args.action == "text":
            if not args.input:
                raise ValueError("--input required")
            result = cmd_text(args.input, args.password)
        elif args.action == "classify":
            if not args.input:
                raise ValueError("--input required")
            result = cmd_classify(args.input, args.password)
        elif args.action == "merge":
            if not args.inputs or len(args.inputs) < 2:
                raise ValueError("--inputs requires at least 2 files")
            if not args.output:
                raise ValueError("--output required")
            result = cmd_merge(args.inputs, args.output)
        elif args.action == "split":
            if not args.input:
                raise ValueError("--input required")
            result = cmd_split(args.input, args.output_dir or "output/split_pages", args.password)
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        _print_human(result, args.action)


def _print_human(data, action):
    if isinstance(data, list):
        for item in data:
            print(f"--- Page {item['page']} ---")
            print(item["text"][:500] if item["text"] else "(empty)")
            print()
        return
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, float):
                print(f"  {k}: {v}")
            else:
                print(f"  {k}: {v}")
        print()
        if action == "classify" and data.get("classification") == "scanned":
            print("⚠️  This appears to be a scanned/image-based PDF (no selectable text).")
            print("   Consider using OCR (e.g. Tesseract) for text extraction.")
        elif action == "classify":
            print("✅ Text-based PDF — text extraction will work.")
        return


if __name__ == "__main__":
    main()