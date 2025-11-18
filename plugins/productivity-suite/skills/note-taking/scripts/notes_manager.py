#!/usr/bin/env python3
"""
Notes Manager for AI-Navigable Second Brain
Part of productivity-skills/note-taking

Handles note operations: add, search, update, index management
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path
import re
from typing import List, Dict, Optional

# Configuration - can be overridden by environment variable
# Default: Prefer OneDrive Documents if available, fall back to local Documents
# This ensures consistency between Claude Desktop and Claude Code on Windows with OneDrive
def get_default_notes_dir() -> Path:
    """Get the default notes directory, preferring OneDrive Documents if it exists"""
    onedrive_docs = Path.home() / 'OneDrive' / 'Documents' / 'notes'
    local_docs = Path.home() / 'Documents' / 'notes'

    # Prefer OneDrive Documents if the OneDrive/Documents folder exists
    if (Path.home() / 'OneDrive' / 'Documents').exists():
        return onedrive_docs
    return local_docs

DEFAULT_NOTES_DIR = get_default_notes_dir()
NOTES_DIR = Path(os.environ.get('NOTES_DIR', DEFAULT_NOTES_DIR)).expanduser().resolve()
INDEX_FILE = NOTES_DIR / '.index.json'
CONFIG_FILE = NOTES_DIR / '.config.json'

def get_current_month_file() -> Path:
    """Get the current month's markdown file path"""
    now = datetime.now()
    month_name = now.strftime("%m-%B")
    year_dir = NOTES_DIR / str(now.year)
    year_dir.mkdir(parents=True, exist_ok=True)
    return year_dir / f"{month_name}.md"

def extract_entries(file_path: Path) -> List[Dict]:
    """Extract all entries from a markdown file"""
    if not file_path.exists():
        return []

    entries = []
    current_entry = None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                # Check if line is a top-level heading (entry start)
                if line.startswith('# ') and not line.startswith('## '):
                    if current_entry:
                        # Filter out file headers (e.g., "Notes - November 2025")
                        if not re.match(r'^Notes - \w+ \d{4}$', current_entry['heading']):
                            entries.append(current_entry)
                    current_entry = {
                        'heading': line.strip('# \n'),
                        'content': '',
                        'file': str(file_path.relative_to(NOTES_DIR)),
                        'date': extract_date_from_file(file_path)
                    }
                elif current_entry:
                    current_entry['content'] += line

        if current_entry:
            # Filter out file headers for the last entry too
            if not re.match(r'^Notes - \w+ \d{4}$', current_entry['heading']):
                entries.append(current_entry)
    except Exception as e:
        print(f"Error reading {file_path}: {e}", file=sys.stderr)

    return entries

def extract_date_from_file(file_path: Path) -> str:
    """Extract date from file path (YYYY/MM-Month.md)"""
    try:
        parts = file_path.parts
        year = parts[-2] if len(parts) >= 2 else str(datetime.now().year)
        month = parts[-1].split('-')[0] if '-' in parts[-1] else '01'
        return f"{year}-{month}-01"
    except:
        return datetime.now().strftime("%Y-%m-%d")

def add_note(heading: str, content: str, category: Optional[str] = None) -> Dict:
    """Add a new note entry to current month's file"""
    month_file = get_current_month_file()

    # Ensure file exists
    if not month_file.exists():
        month_file.touch()
        month_file.write_text("# Notes - " + datetime.now().strftime("%B %Y") + "\n\n")

    # Format the entry with creation timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d")
    entry = f"\n# {heading}\n{content.strip()}\n\n**Created:** {timestamp}\n"

    # Append to file
    with open(month_file, 'a', encoding='utf-8') as f:
        f.write(entry)
    
    # Update index
    update_index()
    
    return {
        'status': 'success',
        'file': str(month_file.relative_to(NOTES_DIR)),
        'heading': heading,
        'path': str(month_file)
    }

def search_notes(query: str, max_results: int = 10) -> List[Dict]:
    """Search for notes matching query across all files"""
    results = []
    query_lower = query.lower()
    query_terms = query_lower.split()
    
    # Search all markdown files in notes directory
    for year_dir in sorted(NOTES_DIR.glob('*/'), reverse=True):
        if year_dir.is_dir() and not year_dir.name.startswith('.'):
            for md_file in sorted(year_dir.glob('*.md'), reverse=True):
                entries = extract_entries(md_file)
                for entry in entries:
                    relevance = calculate_relevance(entry, query_lower, query_terms)
                    if relevance > 0:
                        results.append({
                            'heading': entry['heading'],
                            'content': entry['content'][:300] + '...' if len(entry['content']) > 300 else entry['content'],
                            'file': entry['file'],
                            'date': entry['date'],
                            'relevance': relevance
                        })
    
    # Sort by relevance and limit results
    results.sort(key=lambda x: x['relevance'], reverse=True)
    return results[:max_results]

def calculate_relevance(entry: Dict, query: str, query_terms: List[str]) -> int:
    """Calculate relevance score for search results"""
    score = 0
    heading_lower = entry['heading'].lower()
    content_lower = entry['content'].lower()

    # Exact phrase match in heading (highest priority - overwhelming bonus)
    if query in heading_lower:
        score += 500  # Massively increased to ensure heading matches always win

    # All terms in heading (but not exact phrase)
    elif all(term in heading_lower for term in query_terms):
        score += 100  # Increased from 50

    # Individual terms in heading
    else:
        for term in query_terms:
            if term in heading_lower:
                score += 20

    # Terms in content (capped to prevent overwhelming heading matches)
    content_score = 0
    for term in query_terms:
        content_score += content_lower.count(term) * 5
    # Cap content contribution at 50 points
    score += min(content_score, 50)
    
    # Boost recent entries (reduced to prevent generic entries from ranking too high)
    try:
        date = datetime.fromisoformat(entry['date'])
        days_old = (datetime.now() - date).days
        if days_old < 30:
            score += 10  # Reduced from 20
        elif days_old < 90:
            score += 5   # Reduced from 10
        elif days_old < 180:
            score += 2   # Reduced from 5
    except:
        pass
    
    return score

def append_to_entry(search_term: str, new_content: str) -> Dict:
    """Find an entry and append content to it"""
    results = search_notes(search_term, max_results=5)

    if not results:
        return {
            'status': 'not_found',
            'query': search_term,
            'suggestion': 'No matching entry found. Create a new note?'
        }

    # Require minimum relevance threshold to avoid weak matches
    if results[0]['relevance'] < 50:
        return {
            'status': 'ambiguous',
            'query': search_term,
            'alternatives': [{'heading': r['heading'], 'relevance': r['relevance']} for r in results[:3]],
            'message': 'No strong match found. Please be more specific or use one of these headings.'
        }

    # Use the most relevant result
    target = results[0]
    file_path = NOTES_DIR / target['file']
    
    # Read the file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {'status': 'error', 'message': f"Failed to read file: {e}"}
    
    # Prepare the update with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d")
    update_text = f"\n**Update ({timestamp}):** {new_content.strip()}\n"
    
    # Find the entry and append
    lines = content.split('\n')
    new_lines = []
    in_target = False
    inserted = False
    
    for line in lines:
        new_lines.append(line)
        
        if line.strip() == f"# {target['heading']}":
            in_target = True
        elif in_target and line.startswith('# ') and not line.startswith('## '):
            # Found next entry, insert before it
            new_lines.insert(-1, update_text)
            inserted = True
            in_target = False
    
    if in_target and not inserted:
        # Was the last entry, append at end
        new_lines.append(update_text)
    
    # Write back
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
    except Exception as e:
        return {'status': 'error', 'message': f"Failed to write file: {e}"}
    
    # Update index
    update_index()
    
    return {
        'status': 'success',
        'heading': target['heading'],
        'file': target['file'],
        'alternatives': [r['heading'] for r in results[1:3]] if len(results) > 1 else []
    }

def update_index() -> Dict:
    """Rebuild the search index from all markdown files"""
    index = {
        'entries': [],
        'last_updated': datetime.now().isoformat(),
        'total_files': 0,
        'total_entries': 0
    }
    
    # Scan all markdown files
    file_count = 0
    entry_count = 0
    
    for year_dir in sorted(NOTES_DIR.glob('*/'), reverse=True):
        if year_dir.is_dir() and not year_dir.name.startswith('.'):
            for md_file in sorted(year_dir.glob('*.md')):
                file_count += 1
                entries = extract_entries(md_file)
                entry_count += len(entries)
                
                for entry in entries:
                    # Extract keywords
                    text = entry['heading'] + ' ' + entry['content']
                    words = re.findall(r'\b[a-zA-Z]{3,}\b', text)
                    # Get unique words, excluding common ones
                    common_words = {'the', 'and', 'for', 'that', 'with', 'this', 'from', 'have', 'was', 'were'}
                    keywords = [w for w in set(words) if w.lower() not in common_words][:15]
                    
                    # Extract category if present
                    category = None
                    if ' - ' in entry['heading']:
                        category = entry['heading'].split(' - ')[0].strip()
                    
                    index['entries'].append({
                        'heading': entry['heading'],
                        'file': entry['file'],
                        'date': entry['date'],
                        'category': category,
                        'keywords': keywords[:10],
                        'content_preview': entry['content'][:100].strip()
                    })
    
    index['total_files'] = file_count
    index['total_entries'] = entry_count
    
    # Write index
    try:
        with open(INDEX_FILE, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2)
    except Exception as e:
        return {'status': 'error', 'message': f"Failed to write index: {e}"}
    
    return {
        'status': 'success',
        'total_files': file_count,
        'total_entries': entry_count,
        'index_path': str(INDEX_FILE)
    }

def get_info() -> Dict:
    """Get information about notes directory and configuration"""
    onedrive_path = Path.home() / 'OneDrive' / 'Documents'

    return {
        'status': 'success',
        'notes_dir': str(NOTES_DIR.resolve()),
        'notes_dir_exists': NOTES_DIR.exists(),
        'notes_dir_is_writable': os.access(NOTES_DIR, os.W_OK) if NOTES_DIR.exists() else False,
        'onedrive_detected': onedrive_path.exists(),
        'using_onedrive': str(NOTES_DIR).startswith(str(onedrive_path)),
        'index_file': str(INDEX_FILE),
        'index_exists': INDEX_FILE.exists(),
        'home_dir': str(Path.home()),
        'current_month_file': str(get_current_month_file()),
        'platform': sys.platform,
        'python_version': sys.version
    }

def get_stats() -> Dict:
    """Get statistics about the notes system"""
    try:
        with open(INDEX_FILE, 'r', encoding='utf-8') as f:
            index = json.load(f)
        
        # Calculate category distribution
        categories = {}
        for entry in index.get('entries', []):
            cat = entry.get('category', 'Uncategorized')
            categories[cat] = categories.get(cat, 0) + 1
        
        # Find most common keywords
        all_keywords = []
        for entry in index.get('entries', []):
            all_keywords.extend(entry.get('keywords', []))
        
        keyword_counts = {}
        for kw in all_keywords:
            keyword_counts[kw] = keyword_counts.get(kw, 0) + 1
        
        top_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'status': 'success',
            'total_entries': index.get('total_entries', 0),
            'total_files': index.get('total_files', 0),
            'last_updated': index.get('last_updated'),
            'categories': categories,
            'top_keywords': top_keywords
        }
    except FileNotFoundError:
        return {
            'status': 'no_index',
            'message': 'Index not found. Run reindex command.'
        }
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def clean_index() -> Dict:
    """Safely remove and rebuild search index"""
    try:
        if INDEX_FILE.exists():
            INDEX_FILE.unlink()
            message = 'Removed existing index. Rebuilding...'
        else:
            message = 'No existing index. Building fresh index...'

        reindex_result = update_index()

        return {
            'status': 'success',
            'message': message,
            'reindex_result': reindex_result
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Failed to clean index: {str(e)}'
        }

def validate() -> Dict:
    """Check all note files for issues"""
    issues = []
    files_checked = 0

    try:
        for year_dir in sorted(NOTES_DIR.glob('[0-9]*')):
            if not year_dir.is_dir():
                continue

            for note_file in sorted(year_dir.glob('*.md')):
                files_checked += 1

                try:
                    content = note_file.read_text(encoding='utf-8')

                    # Check for empty files
                    if not content.strip():
                        issues.append({
                            'file': f"{year_dir.name}/{note_file.name}",
                            'issue': 'Empty file',
                            'severity': 'warning'
                        })

                    # Check for proper heading format
                    elif not content.startswith('#'):
                        issues.append({
                            'file': f"{year_dir.name}/{note_file.name}",
                            'issue': 'No top-level heading',
                            'severity': 'info'
                        })

                except UnicodeDecodeError:
                    issues.append({
                        'file': f"{year_dir.name}/{note_file.name}",
                        'issue': 'Not valid UTF-8',
                        'severity': 'error'
                    })
                except Exception as e:
                    issues.append({
                        'file': f"{year_dir.name}/{note_file.name}",
                        'issue': str(e),
                        'severity': 'error'
                    })

        return {
            'status': 'success',
            'files_checked': files_checked,
            'issues_found': len(issues),
            'issues': issues
        }

    except Exception as e:
        return {
            'status': 'error',
            'message': f'Validation failed: {str(e)}'
        }

def migrate(source_dir: str) -> Dict:
    """Import existing markdown files with validation and indexing"""
    try:
        source = Path(source_dir).expanduser().resolve()

        if not source.exists():
            return {
                'status': 'error',
                'message': f'Source directory not found: {source}'
            }

        if not source.is_dir():
            return {
                'status': 'error',
                'message': f'Source path is not a directory: {source}'
            }

        imported = []
        skipped = []
        errors = []

        for md_file in source.glob('**/*.md'):
            try:
                # Skip hidden files and index
                if md_file.name.startswith('.') or md_file.name == '.index.json':
                    skipped.append(str(md_file.name))
                    continue

                # Read with UTF-8
                content = md_file.read_text(encoding='utf-8')

                if not content.strip():
                    skipped.append(f"{md_file.name} (empty)")
                    continue

                # Use file modification time to determine target year/month
                mtime = datetime.fromtimestamp(md_file.stat().st_mtime)
                year_dir = NOTES_DIR / str(mtime.year)
                year_dir.mkdir(parents=True, exist_ok=True)

                month_name = mtime.strftime('%B')
                month_file = year_dir / f"{mtime.month:02d}-{month_name}.md"

                # Append with separator if file exists
                mode = 'a' if month_file.exists() else 'w'
                with open(month_file, mode, encoding='utf-8') as f:
                    if mode == 'a':
                        f.write('\n\n')
                    f.write(content)
                    if not content.endswith('\n'):
                        f.write('\n')

                imported.append({
                    'source': md_file.name,
                    'destination': f"{mtime.year}/{month_file.name}"
                })

            except Exception as e:
                errors.append({
                    'file': md_file.name,
                    'error': str(e)
                })

        # Rebuild index after migration
        reindex_result = update_index()

        return {
            'status': 'success' if not errors else 'partial',
            'imported': len(imported),
            'skipped': len(skipped),
            'errors': len(errors),
            'details': {
                'imported_files': imported,
                'skipped_files': skipped,
                'errors': errors
            },
            'index_rebuilt': reindex_result.get('status') == 'success'
        }

    except Exception as e:
        return {
            'status': 'error',
            'message': f'Migration failed: {str(e)}'
        }

def main():
    """Main entry point"""
    # Read command from stdin or command line
    if not sys.stdin.isatty():
        try:
            data = json.load(sys.stdin)
        except json.JSONDecodeError:
            data = {'command': 'help'}
    elif len(sys.argv) > 1:
        data = {'command': sys.argv[1]}
    else:
        data = {'command': 'help'}

    command = data.get('command', 'help')

    # Execute command
    if command == 'add':
        result = add_note(
            data.get('heading', 'Untitled'),
            data.get('content', ''),
            data.get('category')
        )
    elif command == 'search':
        result = search_notes(
            data.get('query', ''),
            data.get('max_results', 10)
        )
    elif command == 'append':
        result = append_to_entry(
            data.get('search_term', ''),
            data.get('content', '')
        )
    elif command == 'reindex':
        result = update_index()
    elif command == 'stats':
        result = get_stats()
    elif command == 'info':
        result = get_info()
    elif command == 'clean-index':
        result = clean_index()
    elif command == 'validate':
        result = validate()
    elif command == 'migrate':
        result = migrate(data.get('source_dir', ''))
    else:
        result = {
            'status': 'help',
            'commands': {
                'add': 'Add a new note',
                'search': 'Search for notes',
                'append': 'Append to existing note',
                'reindex': 'Rebuild search index',
                'clean-index': 'Safely remove and rebuild index',
                'validate': 'Check note files for issues',
                'migrate': 'Import existing markdown files',
                'stats': 'Get notes statistics',
                'info': 'Get notes directory info and paths'
            },
            'usage': 'echo \'{"command":"search","query":"test"}\' | python3 notes_manager.py'
        }

    # Output result as JSON
    print(json.dumps(result, indent=2))
    return 0

if __name__ == '__main__':
    sys.exit(main())
