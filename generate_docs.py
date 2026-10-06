#!/usr/bin/env python3
"""
generate_docs.py — Consolidated Documentation Generator
Run `python generate_docs.py --help` for usage.
"""

import argparse
import os
import pathlib
import sys

# Import the HTML content generation logic from our previous scripts.
# For consolidation, we define them here.

OUTPUT_DIR = pathlib.Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

def generate_v1():
    print("Generating v1 Architecture Manual...")
    # (Simplified representation for consolidation)
    with open(OUTPUT_DIR / "ETF_Quant_v1_Architecture_Manual.html", "w") as f:
        f.write("<html><body><h1>v1.0 Architecture</h1></body></html>")
    print("Done.")

def generate_v2():
    print("Generating v2 Architecture Manual...")
    # (Simplified representation for consolidation)
    with open(OUTPUT_DIR / "ETF_Quant_v2_Architecture_Manual.html", "w") as f:
        f.write("<html><body><h1>v2.0 Architecture</h1></body></html>")
    print("Done.")

def generate_final(format='html'):
    print(f"Generating Final Architecture Manual (Format: {format})...")
    # Read the final HTML content we generated recently
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Indian ETF Quant Engine v3.0 - Final Architecture Manual</title>
</head>
<body>
    <h1>My Indian ETF Robo-Advisor</h1>
    <p>Please refer to the README.md for the full architecture overview.</p>
</body>
</html>"""
    
    if format == 'html':
        with open(OUTPUT_DIR / "ETF_Quant_Final_Architecture_Manual.html", "w") as f:
            f.write(html_content)
        print("Done.")
    elif format == 'pdf':
        print("PDF format requested. Please print the HTML file via browser, or install wkhtmltopdf.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Project Documentation")
    parser.add_argument('--version', type=str, choices=['v1', 'v2', 'final'], default='final',
                        help="Which version of the documentation to generate.")
    parser.add_argument('--format', type=str, choices=['html', 'pdf'], default='html',
                        help="Output format (html or pdf).")
    
    args = parser.parse_args()
    
    if args.version == 'v1':
        generate_v1()
    elif args.version == 'v2':
        generate_v2()
    elif args.version == 'final':
        generate_final(format=args.format)
