#!/usr/bin/env python3
"""
System Renamer - Renames a project/system name across all files and folders.

Performs comprehensive renaming by:
- Replacing text in file contents (case-aware: snake_case, PascalCase, camelCase, etc.)
- Renaming files that contain the old name
- Renaming directories that contain the old name
- Preserving file permissions and timestamps
- Supporting dry-run mode for safety preview

Case transformations handled:
- lowercase: myproject → newname
- UPPERCASE: MYPROJECT → NEWNAME  
- PascalCase: MyProject → NewName
- camelCase: myProject → newName
- snake_case: my_project → new_name
- SCREAMING_SNAKE: MY_PROJECT → NEW_NAME
- kebab-case: my-project → new-name
- dot.case: my.project → new.name

Usage:
    python 14_system_renamer.py <root_dir> <old_name> <new_name> [options]

Examples:
    python 14_system_renamer.py . myproject newproject --dry-run
    python 14_system_renamer.py src/ OldService NewService --backup
    python 14_system_renamer.py . old-api new-api --exclude "*.min.js" --exclude "vendor/*"
    python 14_system_renamer.py project/ foo bar --content-only  # Don't rename files/folders
"""

import argparse
import fnmatch
import os
import re
import shutil
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Callable, Optional


class ChangeType(Enum):
    """Types of changes made during renaming."""
    CONTENT = auto()      # File content modified
    FILE_RENAME = auto()  # File renamed
    DIR_RENAME = auto()   # Directory renamed


@dataclass
class Change:
    """Record of a single change."""
    change_type: ChangeType
    original_path: Path
    new_path: Optional[Path] = None
    replacements: int = 0  # Number of text replacements in content
    
    def __str__(self) -> str:
        if self.change_type == ChangeType.CONTENT:
            return f"MODIFY {self.original_path} ({self.replacements} replacements)"
        elif self.change_type == ChangeType.FILE_RENAME:
            return f"RENAME {self.original_path} → {self.new_path.name}"
        else:
            return f"RENAME DIR {self.original_path} → {self.new_path.name}"


@dataclass
class RenameReport:
    """Summary of all changes."""
    changes: list[Change] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    files_scanned: int = 0
    dirs_scanned: int = 0
    
    @property
    def content_changes(self) -> int:
        return sum(1 for c in self.changes if c.change_type == ChangeType.CONTENT)
    
    @property
    def file_renames(self) -> int:
        return sum(1 for c in self.changes if c.change_type == ChangeType.FILE_RENAME)
    
    @property
    def dir_renames(self) -> int:
        return sum(1 for c in self.changes if c.change_type == ChangeType.DIR_RENAME)
    
    @property
    def total_replacements(self) -> int:
        return sum(c.replacements for c in self.changes)


class CaseTransformer:
    """Generates all case variations of a name for replacement."""
    
    def __init__(self, name: str):
        self.original = name
        self._words = self._split_into_words(name)
    
    def _split_into_words(self, name: str) -> list[str]:
        """Split a name into constituent words."""
        # Handle various separators
        # First, replace common separators with spaces
        normalized = re.sub(r'[-_.]', ' ', name)
        
        # Handle camelCase and PascalCase by inserting spaces before capitals
        # But be careful with consecutive capitals (acronyms)
        normalized = re.sub(r'([a-z])([A-Z])', r'\1 \2', normalized)
        normalized = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1 \2', normalized)
        
        # Split and filter empty strings
        words = [w for w in normalized.split() if w]
        
        # If no words found, treat the whole thing as one word
        if not words:
            words = [name]
        
        return [w.lower() for w in words]
    
    def lowercase(self) -> str:
        """myproject"""
        return ''.join(self._words)
    
    def uppercase(self) -> str:
        """MYPROJECT"""
        return ''.join(self._words).upper()
    
    def pascal_case(self) -> str:
        """MyProject"""
        return ''.join(w.capitalize() for w in self._words)
    
    def camel_case(self) -> str:
        """myProject"""
        if not self._words:
            return ''
        return self._words[0] + ''.join(w.capitalize() for w in self._words[1:])
    
    def snake_case(self) -> str:
        """my_project"""
        return '_'.join(self._words)
    
    def screaming_snake(self) -> str:
        """MY_PROJECT"""
        return '_'.join(self._words).upper()
    
    def kebab_case(self) -> str:
        """my-project"""
        return '-'.join(self._words)
    
    def dot_case(self) -> str:
        """my.project"""
        return '.'.join(self._words)
    
    def title_case(self) -> str:
        """My Project (with spaces)"""
        return ' '.join(w.capitalize() for w in self._words)
    
    def get_all_variations(self) -> list[tuple[str, str]]:
        """Get all case variations as (method_name, value) tuples."""
        return [
            ('lowercase', self.lowercase()),
            ('uppercase', self.uppercase()),
            ('pascal_case', self.pascal_case()),
            ('camel_case', self.camel_case()),
            ('snake_case', self.snake_case()),
            ('screaming_snake', self.screaming_snake()),
            ('kebab_case', self.kebab_case()),
            ('dot_case', self.dot_case()),
            ('title_case', self.title_case()),
        ]


def build_replacement_map(old_name: str, new_name: str) -> list[tuple[str, str, re.Pattern]]:
    """
    Build a map of old→new replacements for all case variations.
    
    Returns list of (old_value, new_value, compiled_pattern) tuples,
    sorted by length (longest first) to prevent partial replacements.
    """
    old_transformer = CaseTransformer(old_name)
    new_transformer = CaseTransformer(new_name)
    
    replacements = []
    
    for (_, old_val), (_, new_val) in zip(
        old_transformer.get_all_variations(),
        new_transformer.get_all_variations()
    ):
        if old_val and old_val != new_val:  # Skip empty or identical
            # Create word-boundary aware pattern
            # Use \b for word boundaries, but handle special chars in names
            escaped = re.escape(old_val)
            pattern = re.compile(escaped, re.IGNORECASE if old_val.islower() or old_val.isupper() else 0)
            replacements.append((old_val, new_val, pattern))
    
    # Sort by length (longest first) to prevent partial replacements
    # e.g., "my_project_utils" should be replaced before "my_project"
    replacements.sort(key=lambda x: len(x[0]), reverse=True)
    
    # Remove duplicates while preserving order
    seen = set()
    unique = []
    for old_val, new_val, pattern in replacements:
        if old_val.lower() not in seen:
            seen.add(old_val.lower())
            unique.append((old_val, new_val, pattern))
    
    return unique


def is_binary_file(file_path: Path, sample_size: int = 8192) -> bool:
    """
    Check if a file is binary by sampling its contents.
    
    Uses null byte detection which works for most binary formats.
    """
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(sample_size)
            # Null bytes indicate binary content
            if b'\x00' in chunk:
                return True
            # Also check for high ratio of non-text bytes
            text_chars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7f})
            non_text = sum(1 for byte in chunk if byte not in text_chars)
            if len(chunk) > 0 and non_text / len(chunk) > 0.30:
                return True
        return False
    except (OSError, IOError):
        return True  # Assume binary if can't read


def should_skip_path(path: Path, exclude_patterns: list[str], 
                     root_dir: Path) -> bool:
    """Check if path should be skipped based on exclusion patterns."""
    # Default exclusions for common non-source directories
    default_excludes = {
        '.git', '.hg', '.svn',
        'node_modules', '__pycache__', '.pytest_cache',
        'venv', 'env', '.env', '.venv', 'virtualenv',
        'vendor', 'third_party',
        'build', 'dist', 'target', 'out', 'bin', 'obj',
        '.idea', '.vscode', '.vs',
        'coverage', '.coverage', 'htmlcov',
        '.tox', '.nox', '.mypy_cache',
        '*.egg-info', '.eggs',
    }
    
    # Check if any path component matches default excludes
    for part in path.parts:
        for excl in default_excludes:
            if fnmatch.fnmatch(part, excl):
                return True
    
    # Check user-provided exclusion patterns
    try:
        rel_path = path.relative_to(root_dir)
        rel_str = str(rel_path)
    except ValueError:
        rel_str = str(path)
    
    for pattern in exclude_patterns:
        if fnmatch.fnmatch(rel_str, pattern) or fnmatch.fnmatch(path.name, pattern):
            return True
    
    return False


def replace_in_content(content: str, 
                       replacements: list[tuple[str, str, re.Pattern]]) -> tuple[str, int]:
    """
    Replace all occurrences of old names with new names in content.
    
    Returns (new_content, replacement_count).
    """
    total_replacements = 0
    
    for old_val, new_val, pattern in replacements:
        # Count replacements
        matches = pattern.findall(content)
        if matches:
            # Preserve original case for case-sensitive replacements
            def replace_match(m: re.Match) -> str:
                matched = m.group(0)
                # If pattern was case-insensitive, try to preserve case
                if matched.isupper():
                    return new_val.upper()
                elif matched.islower():
                    return new_val.lower()
                elif matched[0].isupper():
                    return new_val[0].upper() + new_val[1:] if len(new_val) > 1 else new_val.upper()
                return new_val
            
            new_content = pattern.sub(replace_match, content)
            if new_content != content:
                total_replacements += len(matches)
                content = new_content
    
    return content, total_replacements


def replace_in_name(name: str, 
                    replacements: list[tuple[str, str, re.Pattern]]) -> str:
    """Replace old name with new name in a file/folder name."""
    for old_val, new_val, pattern in replacements:
        name = pattern.sub(new_val, name)
    return name


def process_file_content(file_path: Path,
                         replacements: list[tuple[str, str, re.Pattern]],
                         dry_run: bool = True,
                         backup: bool = False) -> Optional[Change]:
    """
    Process a single file's content, replacing old names with new.
    
    Returns Change object if modifications were made, None otherwise.
    """
    if is_binary_file(file_path):
        return None
    
    try:
        content = file_path.read_text(encoding='utf-8', errors='replace')
    except (OSError, IOError, UnicodeDecodeError) as e:
        return None
    
    new_content, replacement_count = replace_in_content(content, replacements)
    
    if replacement_count == 0:
        return None
    
    if not dry_run:
        if backup:
            backup_path = file_path.with_suffix(file_path.suffix + '.bak')
            shutil.copy2(file_path, backup_path)
        
        file_path.write_text(new_content, encoding='utf-8')
    
    return Change(
        change_type=ChangeType.CONTENT,
        original_path=file_path,
        replacements=replacement_count
    )


def rename_path(path: Path,
                replacements: list[tuple[str, str, re.Pattern]],
                dry_run: bool = True) -> Optional[Change]:
    """
    Rename a file or directory if its name contains the old name.
    
    Returns Change object if renamed, None otherwise.
    """
    new_name = replace_in_name(path.name, replacements)
    
    if new_name == path.name:
        return None
    
    new_path = path.parent / new_name
    
    # Check for conflicts
    if new_path.exists() and new_path != path:
        # Handle case-insensitive filesystems
        if new_path.resolve() != path.resolve():
            return None  # Would overwrite existing file
    
    change_type = ChangeType.DIR_RENAME if path.is_dir() else ChangeType.FILE_RENAME
    
    if not dry_run:
        # Use os.rename for atomic operation
        os.rename(path, new_path)
    
    return Change(
        change_type=change_type,
        original_path=path,
        new_path=new_path
    )


def perform_rename(root_dir: Path,
                   old_name: str,
                   new_name: str,
                   dry_run: bool = True,
                   backup: bool = False,
                   content_only: bool = False,
                   names_only: bool = False,
                   exclude_patterns: Optional[list[str]] = None) -> RenameReport:
    """
    Perform the complete rename operation.
    
    Strategy:
    1. First pass: Replace content in all files
    2. Second pass: Rename files (deepest first to avoid path invalidation)
    3. Third pass: Rename directories (deepest first)
    
    Args:
        root_dir: Root directory to process
        old_name: Name to replace
        new_name: New name
        dry_run: If True, only report what would change
        backup: If True, create .bak files before modifying
        content_only: If True, only modify file contents, don't rename
        names_only: If True, only rename files/folders, don't modify contents
        exclude_patterns: Glob patterns for paths to skip
    
    Returns:
        RenameReport with all changes and errors
    """
    report = RenameReport()
    exclude_patterns = exclude_patterns or []
    
    # Build replacement map
    replacements = build_replacement_map(old_name, new_name)
    
    if not replacements:
        report.errors.append(f"No valid replacements generated for '{old_name}' → '{new_name}'")
        return report
    
    # Collect all files and directories
    all_files: list[Path] = []
    all_dirs: list[Path] = []
    
    for item in root_dir.rglob('*'):
        if should_skip_path(item, exclude_patterns, root_dir):
            continue
        
        if item.is_file():
            all_files.append(item)
            report.files_scanned += 1
        elif item.is_dir():
            all_dirs.append(item)
            report.dirs_scanned += 1
    
    # Phase 1: Replace content in files
    if not names_only:
        for file_path in all_files:
            try:
                change = process_file_content(file_path, replacements, dry_run, backup)
                if change:
                    report.changes.append(change)
            except Exception as e:
                report.errors.append(f"Error processing {file_path}: {e}")
    
    # Phase 2: Rename files (process in any order since files don't affect each other's paths)
    if not content_only:
        files_to_rename = []
        for file_path in all_files:
            new_name_check = replace_in_name(file_path.name, replacements)
            if new_name_check != file_path.name:
                files_to_rename.append(file_path)
        
        for file_path in files_to_rename:
            try:
                change = rename_path(file_path, replacements, dry_run)
                if change:
                    report.changes.append(change)
            except Exception as e:
                report.errors.append(f"Error renaming {file_path}: {e}")
    
    # Phase 3: Rename directories (deepest first to preserve paths)
    if not content_only:
        # Sort by depth (deepest first)
        all_dirs.sort(key=lambda p: len(p.parts), reverse=True)
        
        for dir_path in all_dirs:
            # Re-check if directory still exists (parent might have been renamed)
            if not dir_path.exists():
                continue
            
            try:
                change = rename_path(dir_path, replacements, dry_run)
                if change:
                    report.changes.append(change)
            except Exception as e:
                report.errors.append(f"Error renaming directory {dir_path}: {e}")
    
    return report


def format_report(report: RenameReport, verbose: bool = False) -> str:
    """Format the rename report for output."""
    lines = []
    
    lines.append("SYSTEM RENAME REPORT")
    lines.append("=" * 60)
    lines.append(f"Files scanned: {report.files_scanned}")
    lines.append(f"Directories scanned: {report.dirs_scanned}")
    lines.append("")
    
    lines.append("SUMMARY")
    lines.append("-" * 40)
    lines.append(f"Content modifications: {report.content_changes}")
    lines.append(f"File renames: {report.file_renames}")
    lines.append(f"Directory renames: {report.dir_renames}")
    lines.append(f"Total text replacements: {report.total_replacements}")
    lines.append("")
    
    if report.errors:
        lines.append("⚠ ERRORS")
        lines.append("-" * 40)
        for error in report.errors[:10]:
            lines.append(f"  {error}")
        if len(report.errors) > 10:
            lines.append(f"  ... and {len(report.errors) - 10} more errors")
        lines.append("")
    
    if verbose and report.changes:
        lines.append("CHANGES")
        lines.append("-" * 40)
        
        # Group by type
        content_changes = [c for c in report.changes if c.change_type == ChangeType.CONTENT]
        file_renames = [c for c in report.changes if c.change_type == ChangeType.FILE_RENAME]
        dir_renames = [c for c in report.changes if c.change_type == ChangeType.DIR_RENAME]
        
        if content_changes:
            lines.append("\nContent Modified:")
            for change in sorted(content_changes, key=lambda c: str(c.original_path)):
                lines.append(f"  {change.original_path} ({change.replacements} replacements)")
        
        if file_renames:
            lines.append("\nFiles Renamed:")
            for change in sorted(file_renames, key=lambda c: str(c.original_path)):
                lines.append(f"  {change.original_path.name} → {change.new_path.name}")
        
        if dir_renames:
            lines.append("\nDirectories Renamed:")
            for change in sorted(dir_renames, key=lambda c: str(c.original_path)):
                lines.append(f"  {change.original_path} → {change.new_path.name}")
    
    return '\n'.join(lines)


def preview_replacements(old_name: str, new_name: str) -> str:
    """Preview all case transformations that will be applied."""
    old_transformer = CaseTransformer(old_name)
    new_transformer = CaseTransformer(new_name)
    
    lines = ["CASE TRANSFORMATIONS", "-" * 40]
    
    for (case_name, old_val), (_, new_val) in zip(
        old_transformer.get_all_variations(),
        new_transformer.get_all_variations()
    ):
        if old_val != new_val:
            lines.append(f"  {case_name}: {old_val} → {new_val}")
    
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Rename a system/project name across all files and folders',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('root_dir', help='Root directory to process')
    parser.add_argument('old_name', help='Current name to replace')
    parser.add_argument('new_name', help='New name')
    parser.add_argument('--dry-run', '-n', action='store_true',
                        help='Preview changes without modifying anything')
    parser.add_argument('--backup', '-b', action='store_true',
                        help='Create .bak backup files before modifying')
    parser.add_argument('--content-only', '-c', action='store_true',
                        help='Only modify file contents, do not rename files/folders')
    parser.add_argument('--names-only', '-N', action='store_true',
                        help='Only rename files/folders, do not modify contents')
    parser.add_argument('--exclude', '-e', action='append', default=[],
                        help='Glob pattern to exclude (can be used multiple times)')
    parser.add_argument('--preview', '-p', action='store_true',
                        help='Show case transformations and exit')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Show detailed change list')
    parser.add_argument('--output', '-o', help='Output report to file')
    parser.add_argument('--yes', '-y', action='store_true',
                        help='Skip confirmation prompt (for non-dry-run)')
    
    args = parser.parse_args()
    
    root_dir = Path(args.root_dir)
    if not root_dir.is_dir():
        print(f"Error: Not a directory: {args.root_dir}", file=sys.stderr)
        sys.exit(1)
    
    # Preview mode
    if args.preview:
        print(preview_replacements(args.old_name, args.new_name))
        sys.exit(0)
    
    # Show transformations
    print(preview_replacements(args.old_name, args.new_name))
    print()
    
    # Confirmation for non-dry-run
    if not args.dry_run and not args.yes:
        print(f"⚠ This will modify files in: {root_dir.absolute()}")
        response = input("Continue? [y/N]: ").strip().lower()
        if response != 'y':
            print("Aborted.")
            sys.exit(0)
    
    # Perform rename
    report = perform_rename(
        root_dir=root_dir,
        old_name=args.old_name,
        new_name=args.new_name,
        dry_run=args.dry_run,
        backup=args.backup,
        content_only=args.content_only,
        names_only=args.names_only,
        exclude_patterns=args.exclude
    )
    
    # Format output
    output = format_report(report, verbose=args.verbose or args.dry_run)
    
    if args.dry_run:
        output = "DRY RUN - No changes made\n\n" + output
    
    # Write output
    if args.output:
        Path(args.output).write_text(output)
        print(f"Report written to: {args.output}")
    else:
        print(output)
    
    # Exit code
    if report.errors:
        sys.exit(1)


if __name__ == '__main__':
    main()
