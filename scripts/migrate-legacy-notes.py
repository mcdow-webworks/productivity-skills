#!/usr/bin/env python3
"""
Legacy Notes Migration Script
Migrates notes from YYYY-MM.md format to YYYY/MM-Month.md with category inference
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

# Month number to name mapping
MONTHS = {
    '01': 'January', '02': 'February', '03': 'March', '04': 'April',
    '05': 'May', '06': 'June', '07': 'July', '08': 'August',
    '09': 'September', '10': 'October', '11': 'November', '12': 'December'
}

# Category inference keywords (lowercase)
CATEGORY_KEYWORDS = {
    'Work': ['develop', 'fix', 'build', 'deploy', 'setup', 'configure', 'move',
             'install', 'update', 'upgrade', 'migrate', 'implement', 'create',
             'debug', 'troubleshoot', 'optimize', 'refactor', 'test', 'release',
             'adapter', 'epublisher', 'aws', 'dns', 'server', 'machine'],
    'Meeting': ['meeting', 'discussion', 'call', 'sync', 'standup', 'retrospective'],
    'Health': ['scan', 'results', 'appointment', 'ct', 'doctor', 'medical', 'health',
               'chest', 'contrast', 'mri', 'xray'],
    'Learning': ['learn', 'tutorial', 'research', 'study', 'skills', 'course',
                 'training', 'documentation', 'guide', 'claude', 'ai'],
    'Idea': ['idea', 'concept', 'proposal', 'brainstorm', 'think', 'consider'],
    'Decision': ['decided', 'chose', 'selected', 'cancel', 'cancelled', 'approved',
                 'rejected', 'accepted'],
    'Task': ['todo', 'task', 'action', 'need to', 'should', 'must'],
}


def infer_category(heading: str) -> str:
    """Infer category from heading text using keyword matching"""
    heading_lower = heading.lower()

    # Check each category's keywords
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in heading_lower for keyword in keywords):
            return category

    # Default category if no matches
    return 'Note'


def process_heading(line: str) -> str:
    """Transform '# Heading' to '# Category - Heading' if not already formatted"""
    # Check if already in "Category - Description" format
    if re.match(r'^# \w+ - ', line):
        return line

    # Extract heading text (remove leading '# ')
    heading_text = line.lstrip('#').strip()

    # Infer category
    category = infer_category(heading_text)

    # Return formatted heading
    return f"# {category} - {heading_text}\n"


def process_file_content(content: str, year: str, month_name: str) -> str:
    """Process file content: add header and transform headings"""
    lines = content.split('\n')
    output_lines = []

    # Add file header
    output_lines.append(f"# Notes - {month_name} {year}\n")
    output_lines.append("\n")

    # Process each line
    for line in lines:
        # Check if line is a top-level heading (not ##)
        if line.startswith('# ') and not line.startswith('## '):
            # Transform heading with category inference
            output_lines.append(process_heading(line))
        else:
            # Keep line as-is
            output_lines.append(line + '\n')

    return ''.join(output_lines)


def migrate_file(source_path: Path, dest_base: Path) -> Tuple[bool, str]:
    """
    Migrate a single YYYY-MM.md file to YYYY/MM-Month.md format
    Returns (success, message)
    """
    # Parse filename (e.g., "2025-11.md")
    filename = source_path.stem  # "2025-11"

    try:
        year, month = filename.split('-')

        if month not in MONTHS:
            return False, f"Invalid month number: {month}"

        month_name = MONTHS[month]

        # Create destination path
        year_dir = dest_base / year
        year_dir.mkdir(parents=True, exist_ok=True)

        dest_path = year_dir / f"{month}-{month_name}.md"

        # Read source file
        with open(source_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Process content
        processed_content = process_file_content(content, year, month_name)

        # Write to destination
        with open(dest_path, 'w', encoding='utf-8') as f:
            f.write(processed_content)

        return True, f"Migrated {filename}.md -> {year}/{month}-{month_name}.md"

    except Exception as e:
        return False, f"Error migrating {filename}.md: {str(e)}"


def main():
    """Main migration function"""
    # Source and destination paths
    source_dir = Path(r"\\Terminus\Users\mcdow\Desktop\Notes")
    dest_dir = Path.home() / 'OneDrive' / 'Documents' / 'notes'

    # Fallback if OneDrive doesn't exist
    if not (Path.home() / 'OneDrive' / 'Documents').exists():
        dest_dir = Path.home() / 'Documents' / 'notes'

    print(f"Source: {source_dir}")
    print(f"Destination: {dest_dir}")
    print()

    # Verify source exists
    if not source_dir.exists():
        print(f"ERROR: Source directory not found: {source_dir}")
        return 1

    # Create destination if needed
    dest_dir.mkdir(parents=True, exist_ok=True)

    # Find all YYYY-MM.md files
    md_files = sorted(source_dir.glob('????-??.md'))

    if not md_files:
        print(f"No YYYY-MM.md files found in {source_dir}")
        return 1

    print(f"Found {len(md_files)} files to migrate:\n")

    # Migrate each file
    success_count = 0
    fail_count = 0

    for source_file in md_files:
        success, message = migrate_file(source_file, dest_dir)
        status = '[OK]' if success else '[FAIL]'
        print(f"{status} {message}")

        if success:
            success_count += 1
        else:
            fail_count += 1

    # Summary
    print()
    print("=" * 60)
    print(f"Migration complete:")
    print(f"  Success: {success_count}")
    print(f"  Failed: {fail_count}")
    print(f"  Total: {len(md_files)}")
    print()
    print(f"Notes migrated to: {dest_dir}")
    print(f"Original files preserved at: {source_dir}")

    return 0 if fail_count == 0 else 1


if __name__ == '__main__':
    exit(main())
