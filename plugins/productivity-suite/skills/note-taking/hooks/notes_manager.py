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
# Default: ~/Documents/notes on all platforms
DEFAULT_NOTES_DIR = Path.home() / 'Documents' / 'notes'
NOTES_DIR = Path(os.environ.get('NOTES_DIR', DEFAULT_NOTES_DIR))
INDEX_FILE = NOTES_DIR / '.index.json'
CONNECTIONS_FILE = NOTES_DIR / '.connections.json'
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
    
    # Format the entry
    entry = f"\n# {heading}\n{content.strip()}\n"
    
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
    
    # Exact match in heading (highest priority)
    if query in heading_lower:
        score += 100
    
    # All terms in heading
    if all(term in heading_lower for term in query_terms):
        score += 50
    
    # Individual terms in heading
    for term in query_terms:
        if term in heading_lower:
            score += 20
    
    # Terms in content
    for term in query_terms:
        score += content_lower.count(term) * 5
    
    # Boost recent entries
    try:
        date = datetime.fromisoformat(entry['date'])
        days_old = (datetime.now() - date).days
        if days_old < 30:
            score += 20
        elif days_old < 90:
            score += 10
        elif days_old < 180:
            score += 5
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
    return {
        'status': 'success',
        'notes_dir': str(NOTES_DIR.resolve()),
        'notes_dir_exists': NOTES_DIR.exists(),
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
    else:
        result = {
            'status': 'help',
            'commands': {
                'add': 'Add a new note',
                'search': 'Search for notes',
                'append': 'Append to existing note',
                'reindex': 'Rebuild search index',
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
