# Report Exports

## Purpose

This document describes the essay report export feature.

## Supported formats

The frontend currently supports:

- Markdown
- Word (`.docx`)
- PDF

## Report contents

Each export should include:

- essay question
- submitted essay
- overall score
- category-by-category score breakdown
- comments and feedback for each category
- deduction reasons
- suggestions for improvement

Where available, the report should also preserve:

- strengths
- detailed category analysis

## Source of report data

Exported reports are generated from the same result payload shown in the frontend.

The main source is the response from:

- [POST /api/grade-essay](./api_specs.md)

## Formatting expectations

Reports should be:

- readable without the app UI
- structured clearly by section
- suitable for revision and study
- consistent across formats as much as possible

The exact styling can differ by format, but the core information should stay aligned.

## Markdown expectations

Markdown exports should be:

- plain and portable
- easy to copy, share, or store in version control
- organized with headings and simple tables where useful

## Word expectations

Word exports should:

- preserve section structure
- remain readable after download
- support common study and annotation workflows

## PDF expectations

PDF exports should:

- render as a stable read-only version
- preserve the main section order and scores
- remain readable on screen and when printed

The preferred PDF path is now:

- Markdown report -> `pandoc` -> PDF

This is intended to preserve layout quality more closely to the Word export.

If `pandoc` is unavailable, the frontend falls back to the built-in ReportLab PDF generator.

## PDF rendering behavior

The app now uses these PDF strategies in order:

1. `pandoc` with an available PDF engine
2. built-in ReportLab fallback

When `pandoc` uses an HTML-capable engine such as `wkhtmltopdf` or `weasyprint`, the app applies the stylesheet in [frontend/assets/report-export.css](../frontend/assets/report-export.css) for improved heading, spacing, and table formatting.

## Limitations

- Export content depends on the current result payload.
- Very long feedback may wrap differently between Word and PDF.
- PDF quality depends on local tools available on the machine.
- Export generation requires the relevant Python dependencies to be installed.

## Dependency notes

Word and PDF exports depend on installed packages from the project environment.

For the best PDF output, install:

- `pandoc`
- a usable PDF engine such as `wkhtmltopdf`, `weasyprint`, `xelatex`, `lualatex`, `pdflatex`, or `tectonic`

You can also configure explicit tool paths in [.env.local](../.env.local):

```env
PANDOC_PATH=/opt/homebrew/bin/pandoc
PDF_ENGINE_PATH=/opt/homebrew/bin/wkhtmltopdf
```

If export features fail or disappear, rerun:

```bash
uv sync
```

## Related files

- [docs/api_specs.md](./api_specs.md)
- [frontend/app.py](../frontend/app.py)
- [docs/feedback_style.md](./feedback_style.md)
