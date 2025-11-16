#!/usr/bin/env python3
"""
Create a properly formatted ZIP file for Claude Desktop skill upload.
Ensures paths use forward slashes (/) not backslashes (\\).
"""

import zipfile
import os
from pathlib import Path

def create_skill_zip(skill_dir, output_zip):
    """Create a ZIP file with forward-slash paths for Claude Desktop."""
    skill_path = Path(skill_dir)

    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add SKILL.md at root
        skill_md = skill_path / 'SKILL.md'
        if skill_md.exists():
            zipf.write(skill_md, 'SKILL.md')
            print(f"Added: SKILL.md")

        # Add all files in hooks/ directory
        hooks_dir = skill_path / 'hooks'
        if hooks_dir.exists():
            for file in hooks_dir.rglob('*'):
                if file.is_file() and not file.name.endswith('.gz'):
                    arcname = f"hooks/{file.relative_to(hooks_dir).as_posix()}"
                    zipf.write(file, arcname)
                    print(f"Added: {arcname}")

        # Add all files in templates/ directory
        templates_dir = skill_path / 'templates'
        if templates_dir.exists():
            for file in templates_dir.rglob('*'):
                if file.is_file() and not file.name.endswith('.gz'):
                    arcname = f"templates/{file.relative_to(templates_dir).as_posix()}"
                    zipf.write(file, arcname)
                    print(f"Added: {arcname}")

    print(f"\nCreated {output_zip}")

    # Verify ZIP contents
    print("\nZIP contents:")
    with zipfile.ZipFile(output_zip, 'r') as zipf:
        for info in zipf.infolist():
            print(f"  {info.filename}")

if __name__ == '__main__':
    skill_directory = 'plugins/productivity-suite/skills/note-taking'
    output_file = 'note-taking-skill.zip'

    create_skill_zip(skill_directory, output_file)
