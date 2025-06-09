#!/bin/bash

# Script to convert Markdown with Mermaid diagrams to PDF
# Usage: ./convert-report.sh input.md output.pdf

set -e

if [ $# -ne 2 ]; then
    echo "Usage: $0 input.md output.pdf"
    echo "Example: $0 report.md report.pdf"
    exit 1
fi

INPUT_MD="$1"
OUTPUT_PDF="$2"
BASENAME=$(basename "$INPUT_MD" .md)

# Temporary files
TEMP_HTML="${BASENAME}_temp.html"
FIXED_HTML="${BASENAME}_fixed.html"

echo "🔄 Converting $INPUT_MD to PDF with Mermaid support..."

# Step 1: Convert Markdown to HTML with custom template
echo "📄 Step 1: Converting Markdown to HTML..."
pandoc "$INPUT_MD" -o "$TEMP_HTML" --template=simple_convert.html -s

# Step 2: Fix Mermaid diagram structure
echo "🔧 Step 2: Fixing Mermaid diagram structure..."
python3 fix_mermaid.py "$TEMP_HTML" "$FIXED_HTML"

# Step 3: Convert HTML to PDF using Chrome
echo "📊 Step 3: Rendering diagrams and creating PDF..."
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
    --headless \
    --disable-gpu \
    --print-to-pdf="$OUTPUT_PDF" \
    --print-to-pdf-no-header \
    --run-all-compositor-stages-before-draw \
    --virtual-time-budget=10000 \
    "file://$(pwd)/$FIXED_HTML"

# Cleanup temporary files
echo "🧹 Step 4: Cleaning up temporary files..."
rm -f "$TEMP_HTML" "$FIXED_HTML"

# Check if PDF was created successfully
if [ -f "$OUTPUT_PDF" ]; then
    FILE_SIZE=$(ls -lh "$OUTPUT_PDF" | awk '{print $5}')
    echo "✅ Success! PDF created: $OUTPUT_PDF ($FILE_SIZE)"
    echo "📋 The PDF includes all Mermaid diagrams rendered as graphics"
else
    echo "❌ Error: PDF creation failed"
    exit 1
fi 