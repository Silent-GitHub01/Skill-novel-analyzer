#!/usr/bin/env python3
"""
Novel Chapter Splitter
======================
Detects chapter boundaries in long-form fiction (Chinese or English) and splits
the text into structured chapters for downstream analysis.

Usage:
    python chapter_splitter.py <input_file> [--output <output_dir>] [--encoding <encoding>]

Output:
    A JSON file (chapters.json) containing an array of chapter objects:
    [
      {
        "index": 0,
        "title": "第一章 风起",
        "start_line": 0,
        "end_line": 150,
        "char_count": 5200,
        "preview": "前200字的预览..."
      },
      ...
    ]

    Individual chapter text files are also written to the output directory
    (chapter_000.txt, chapter_001.txt, ...).
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Chapter heading patterns
# ---------------------------------------------------------------------------

# Chinese chapter heading patterns (ordered by specificity)
CN_PATTERNS = [
    # 第一章 / 第1章 / 第 1 章 / 第一回 / 第一卷
    re.compile(
        r'^[\s]*第[\s]*([零一二三四五六七八九十百千0-9]+)[\s]*(章|回|卷|节|篇|部)[\s]*(.*)$',
        re.MULTILINE
    ),
    # 第01章 (zero-padded numbers)
    re.compile(
        r'^[\s]*第[\s]*(\d{1,4})[\s]*(章|回|卷|节|篇|部)[\s]*(.*)$',
        re.MULTILINE
    ),
    # 序章 / 楔子 / 引子 / 楔 / 引 / 尾声 / 后记 / 番外 / 终章 / 前言 / 序言
    re.compile(
        r'^[\s]*(序章|楔子|引子|楔|引|尾声|后记|番外篇?|终章|前言|序言|序|跋|尾声|完结篇|终卷)[\s]*(.*)$',
        re.MULTILINE
    ),
    # Chapter 1 / Chapter One / CHAPTER I
    re.compile(
        r'^[\s]*Chapter[\s]+([0-9IVXLCDMivxlcdm]+|[A-Za-z]+)[\s*[:.\-—\s]*(.*)$',
        re.MULTILINE | re.IGNORECASE
    ),
    # PART 1 / Part One
    re.compile(
        r'^[\s]*Part[\s]+([0-9IVXLCDMivxlcdm]+|[A-Za-z]+)[\s*[:.\-—\s]*(.*)$',
        re.MULTILINE | re.IGNORECASE
    ),
    # Epilogue / Prologue / Prelude
    re.compile(
        r'^[\s]*(Epilogue|Prologue|Prelude|Afterword|Foreword|Introduction)[\s*[:.\-—\s]*(.*)$',
        re.MULTILINE | re.IGNORECASE
    ),
]

# Fallback: lines that look like short standalone titles (all-caps or enclosed)
FALLBACK_TITLE = re.compile(r'^[\s]*[「「『【](.{2,30})[」」』】][\s]*$')


def detect_encoding(file_path: str) -> str:
    """Try to detect file encoding, defaulting to UTF-8."""
    encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'big5', 'utf-16', 'latin-1']
    for enc in encodings:
        try:
            with open(file_path, 'r', encoding=enc) as f:
                f.read(10240)  # Read first 10KB to test
            return enc
        except (UnicodeDecodeError, UnicodeError):
            continue
    return 'utf-8'  # Fallback


def read_text(file_path: str) -> str:
    """Read text file with auto-detected encoding."""
    enc = detect_encoding(file_path)
    with open(file_path, 'r', encoding=enc) as f:
        return f.read()


def normalize_cn_number(num_str: str) -> int:
    """Convert Chinese numeral string to integer."""
    cn_map = {
        '零': 0, '〇': 0, '一': 1, '二': 2, '三': 3, '四': 4,
        '五': 5, '六': 6, '七': 7, '八': 8, '九': 9,
        '十': 10, '百': 100, '千': 1000,
    }
    # If it's already a number
    if num_str.isdigit():
        return int(num_str)

    # Handle Chinese numerals
    if not any(c in cn_map for c in num_str):
        return 0

    result = 0
    temp = 0
    for char in num_str:
        if char not in cn_map:
            return 0
        val = cn_map[char]
        if val >= 10:
            if temp == 0:
                temp = 1
            result += temp * val
            temp = 0
        else:
            temp = val
    result += temp
    return result


def find_chapter_boundaries(text: str) -> list:
    """
    Find all chapter heading positions in the text.
    Returns a list of (line_number, matched_title, pattern_index) tuples.
    """
    lines = text.split('\n')
    boundaries = []

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or len(stripped) > 100:
            continue  # Skip empty or overly long lines

        for pat_idx, pattern in enumerate(CN_PATTERNS):
            match = pattern.match(stripped)
            if match:
                # Reconstruct a clean title
                groups = match.groups()
                if groups and groups[0]:
                    # Has a number/ordinal
                    title = stripped.strip()
                else:
                    title = stripped.strip()
                boundaries.append((i, title, pat_idx))
                break  # Only match first pattern per line

    return boundaries


def split_into_chapters(text: str) -> list:
    """
    Split text into chapters based on detected boundaries.
    Returns list of dicts: {index, title, start_line, end_line, char_count, text, preview}
    """
    lines = text.split('\n')
    boundaries = find_chapter_boundaries(text)

    if not boundaries or len(boundaries) < 2:
        # No clear chapter structure found; treat entire text as one chunk
        # But try to split by large text blocks if it's very long
        total_lines = len(lines)
        if total_lines > 500:
            # Split into roughly equal chunks of ~200 lines
            chunk_size = 200
            chunks = []
            for i in range(0, total_lines, chunk_size):
                chunk_lines = lines[i:i + chunk_size]
                chunk_text = '\n'.join(chunk_lines)
                chunks.append({
                    'index': len(chunks),
                    'title': f'片段 {len(chunks) + 1}',
                    'start_line': i,
                    'end_line': min(i + chunk_size - 1, total_lines - 1),
                    'char_count': len(chunk_text),
                    'text': chunk_text,
                    'preview': chunk_text[:200].replace('\n', ' '),
                })
            return chunks
        else:
            return [{
                'index': 0,
                'title': '全文',
                'start_line': 0,
                'end_line': total_lines - 1,
                'char_count': len(text),
                'text': text,
                'preview': text[:200].replace('\n', ' '),
            }]

    chapters = []
    for idx, (start_line, title, pat_idx) in enumerate(boundaries):
        if idx + 1 < len(boundaries):
            end_line = boundaries[idx + 1][0] - 1
        else:
            end_line = len(lines) - 1

        chapter_lines = lines[start_line:end_line + 1]
        chapter_text = '\n'.join(chapter_lines)

        chapters.append({
            'index': idx,
            'title': title,
            'start_line': start_line,
            'end_line': end_line,
            'char_count': len(chapter_text),
            'text': chapter_text,
            'preview': chapter_text[:200].replace('\n', ' '),
        })

    return chapters


def deduplicate_chapters(chapters: list) -> list:
    """Remove near-duplicate or empty chapters, re-index."""
    filtered = [ch for ch in chapters if ch['char_count'] > 50]
    for i, ch in enumerate(filtered):
        ch['index'] = i
    return filtered


def write_output(chapters: list, output_dir: str, input_name: str):
    """Write chapters.json and individual chapter files."""
    os.makedirs(output_dir, exist_ok=True)

    # Write metadata JSON (without full text to keep it manageable)
    meta = []
    for ch in chapters:
        meta.append({
            'index': ch['index'],
            'title': ch['title'],
            'start_line': ch['start_line'],
            'end_line': ch['end_line'],
            'char_count': ch['char_count'],
            'preview': ch['preview'],
        })

    json_path = os.path.join(output_dir, f'{input_name}_chapters.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    # Write individual chapter files
    for ch in chapters:
        ch_path = os.path.join(output_dir, f'{input_name}_chapter_{ch["index"]:03d}.txt')
        with open(ch_path, 'w', encoding='utf-8') as f:
            f.write(ch['text'])

    # Write full structured JSON (with text) for downstream processing
    full_path = os.path.join(output_dir, f'{input_name}_chapters_full.json')
    with open(full_path, 'w', encoding='utf-8') as f:
        json.dump(chapters, f, ensure_ascii=False, indent=2)

    return json_path, full_path


def main():
    parser = argparse.ArgumentParser(
        description='Split a novel text file into chapters for analysis.'
    )
    parser.add_argument('input_file', help='Path to the novel text file')
    parser.add_argument(
        '--output', '-o',
        default=None,
        help='Output directory (default: same directory as input file)'
    )
    parser.add_argument(
        '--encoding', '-e',
        default=None,
        help='Force file encoding (default: auto-detect)'
    )

    args = parser.parse_args()

    if not os.path.isfile(args.input_file):
        print(f'Error: File not found: {args.input_file}', file=sys.stderr)
        sys.exit(1)

    # Read text
    if args.encoding:
        with open(args.input_file, 'r', encoding=args.encoding) as f:
            text = f.read()
    else:
        text = read_text(args.input_file)

    print(f'Read {len(text)} characters from {args.input_file}')

    # Split into chapters
    chapters = split_into_chapters(text)
    chapters = deduplicate_chapters(chapters)

    print(f'Detected {len(chapters)} chapters/sections')

    # Print summary
    for ch in chapters:
        print(f'  [{ch["index"]:3d}] {ch["title"][:50]:<50s}  ({ch["char_count"]:>6d} chars)')

    # Write output
    input_name = Path(args.input_file).stem
    output_dir = args.output or os.path.dirname(os.path.abspath(args.input_file))
    json_path, full_path = write_output(chapters, output_dir, input_name)

    print(f'\nOutput:')
    print(f'  Metadata:  {json_path}')
    print(f'  Full data: {full_path}')
    print(f'  Chapter files: {output_dir}/{input_name}_chapter_*.txt')


if __name__ == '__main__':
    main()
