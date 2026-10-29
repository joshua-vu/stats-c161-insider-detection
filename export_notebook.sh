#!/usr/bin/env bash
# Quick script to export any Jupyter Notebook to a cleanly styled PDF
set -e

INPUT_NOTEBOOK="${1:-insider_eda_presentation.ipynb}"

if [ ! -f "$INPUT_NOTEBOOK" ]; then
    echo "Error: Notebook file '$INPUT_NOTEBOOK' not found."
    echo "Usage: ./export_notebook.sh <path/to/notebook.ipynb> [output.pdf]"
    exit 1
fi

BASENAME=$(basename "$INPUT_NOTEBOOK" .ipynb)
OUTPUT_PDF="${2:-$HOME/Downloads/${BASENAME}.pdf}"

TMP_CSS="/tmp/nb_pdf_style_$$.css"
TMP_HTML="/tmp/nb_pdf_$$.html"
TMP_CHROME_DIR="/tmp/chrome_pdf_tmp_$$"

# 1. Clean notebook printing stylesheet
cat << 'EOF' > "$TMP_CSS"
@page {
  size: letter;
  margin: 16mm 14mm 16mm 14mm;
}
@media print {
  body {
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }
}
html, body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  font-size: 12.5px;
  line-height: 1.55;
  color: #24292f;
  background-color: #ffffff;
  margin: 0;
  padding: 0;
  max-width: 100% !important;
}
h1, h2, h3, h4, h5, h6 {
  color: #1f2328;
  font-weight: 600;
  margin-top: 24px;
  margin-bottom: 12px;
  page-break-after: avoid;
  break-after: avoid;
}
h1 {
  font-size: 1.85em;
  padding-bottom: 0.3em;
  border-bottom: 1.5px solid #d8dee4;
  margin-top: 0;
}
h2 {
  font-size: 1.4em;
  padding-bottom: 0.25em;
  border-bottom: 1px solid #d8dee4;
}
h3 { font-size: 1.2em; }
p, ul, ol, blockquote { margin-top: 0; margin-bottom: 10px; }
code:not([class*="sourceCode"]) {
  font-family: "SFMono-Regular", Menlo, Monaco, Consolas, "Liberation Mono", monospace;
  font-size: 0.88em;
  background-color: #eff1f3;
  padding: 0.15em 0.35em;
  border-radius: 4px;
  color: #0969da;
}
div.sourceCode {
  margin: 12px 0 6px 0;
  background-color: #f6f8fa;
  border: 1px solid #d0d7de;
  border-left: 3.5px solid #0969da;
  border-radius: 6px;
  padding: 8px 12px;
  page-break-inside: avoid;
  break-inside: avoid;
}
div.sourceCode pre {
  margin: 0;
  padding: 0;
  font-family: "SFMono-Regular", Menlo, Monaco, Consolas, monospace;
  font-size: 11px;
  line-height: 1.45;
  background: transparent;
}
div.output { margin: 4px 0 14px 0; page-break-inside: avoid; break-inside: avoid; }
div.output.stream.stdout {
  background-color: #fafbfc;
  border: 1px solid #e1e4e8;
  border-left: 3.5px solid #8c959f;
  border-radius: 4px;
  padding: 8px 12px;
}
div.output.stream.stdout pre, div.output.execute_result pre {
  margin: 0;
  font-family: "SFMono-Regular", Menlo, Monaco, Consolas, monospace;
  font-size: 10.5px;
  line-height: 1.4;
  white-space: pre-wrap;
  word-break: break-all;
}
table {
  border-collapse: collapse;
  width: auto;
  max-width: 100%;
  margin: 10px 0;
  font-size: 11px;
  page-break-inside: avoid;
  break-inside: avoid;
}
table, th, td { border: 1px solid #d0d7de; }
th {
  background-color: #f6f8fa;
  font-weight: 600;
  padding: 6px 10px;
  text-align: left;
}
td { padding: 5px 10px; }
tbody tr:nth-child(even) { background-color: #fcfcfd; }
img {
  max-width: 95% !important;
  height: auto;
  display: block;
  margin: 14px auto;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  page-break-inside: avoid;
  break-inside: avoid;
}
EOF

# 2. Convert to standalone HTML with embedded images
echo "Converting $INPUT_NOTEBOOK to HTML..."
/usr/local/bin/pandoc "$INPUT_NOTEBOOK" \
  --css "$TMP_CSS" \
  --embed-resources \
  --standalone \
  --highlight-style=pygments \
  -o "$TMP_HTML" 2>/dev/null

# 3. Print to PDF using Headless Chrome
echo "Rendering PDF with Chrome..."
mkdir -p "$TMP_CHROME_DIR"
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=new \
  --no-sandbox \
  --disable-gpu \
  --disable-crash-reporter \
  --user-data-dir="$TMP_CHROME_DIR" \
  --no-pdf-header-footer \
  --print-to-pdf="$OUTPUT_PDF" \
  "$TMP_HTML" >/dev/null 2>&1 || true

# 4. Clean up
rm -rf "$TMP_CSS" "$TMP_HTML" "$TMP_CHROME_DIR"

if [ -f "$OUTPUT_PDF" ]; then
    echo "✅ Successfully exported to: $OUTPUT_PDF"
else
    echo "❌ Export failed."
    exit 1
fi

