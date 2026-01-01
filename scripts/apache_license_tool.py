#!/usr/bin/env python3
# Copyright 2025 Michael Maillet, Damien Davison, and Sacha Davison
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Apache 2.0 License Management Tool for Symbo

Automates:
  1. NOTICE file creation (required by Apache 2.0)
  2. License header injection into source files

Usage:
  python apache_license_tool.py /path/to/repo
  python apache_license_tool.py /path/to/repo --dry-run
  python apache_license_tool.py /path/to/repo --backup
"""

from __future__ import annotations

import argparse
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable

# =============================================================================
# Configuration — Symbo / Recursive AI Devs
# =============================================================================

COPYRIGHT_YEAR = "2025"
COPYRIGHT_HOLDERS = "Damien Davison & Michael Maillet"
ORGANIZATION = "Recursive AI Devs"
PROJECT_NAME = "Symbo"
PROJECT_DESCRIPTION = "A Hybrid Generative Symbolic Reasoning Engine"

NOTICE_CONTENT = f"""{PROJECT_NAME} — {PROJECT_DESCRIPTION}
Copyright {COPYRIGHT_YEAR} {COPYRIGHT_HOLDERS}
{ORGANIZATION}

This product includes software developed by {ORGANIZATION}.
"""

LICENSE_HEADER_TEMPLATE = f"""Copyright {COPYRIGHT_YEAR} {COPYRIGHT_HOLDERS}, {ORGANIZATION}

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License."""


# =============================================================================
# File Type Definitions
# =============================================================================

@dataclass(frozen=True)
class CommentStyle:
    """Defines how comments are formatted for a given file type."""
    line_prefix: str
    block_start: str | None = None
    block_end: str | None = None
    preserve_shebang: bool = False
    
    def format_header(self, header_text: str) -> str:
        """Format the license header using this comment style."""
        lines = header_text.strip().split("\n")
        
        if self.block_start and self.block_end:
            # Block comment style (C, Java, Rust, etc.)
            formatted_lines = [self.block_start]
            for line in lines:
                if line.strip():
                    formatted_lines.append(f" * {line}")
                else:
                    formatted_lines.append(" *")
            formatted_lines.append(f" {self.block_end}")
            return "\n".join(formatted_lines)
        else:
            # Line comment style (Python, Shell, etc.)
            formatted_lines = []
            for line in lines:
                if line.strip():
                    formatted_lines.append(f"{self.line_prefix} {line}")
                else:
                    formatted_lines.append(self.line_prefix)
            return "\n".join(formatted_lines)


# Comment styles for different file types
COMMENT_STYLES: dict[str, CommentStyle] = {
    # Line-comment languages
    ".py": CommentStyle(line_prefix="#", preserve_shebang=True),
    ".pyi": CommentStyle(line_prefix="#"),
    ".sh": CommentStyle(line_prefix="#", preserve_shebang=True),
    ".bash": CommentStyle(line_prefix="#", preserve_shebang=True),
    ".zsh": CommentStyle(line_prefix="#", preserve_shebang=True),
    ".rb": CommentStyle(line_prefix="#", preserve_shebang=True),
    ".pl": CommentStyle(line_prefix="#", preserve_shebang=True),
    ".r": CommentStyle(line_prefix="#"),
    ".R": CommentStyle(line_prefix="#"),
    ".yaml": CommentStyle(line_prefix="#"),
    ".yml": CommentStyle(line_prefix="#"),
    ".toml": CommentStyle(line_prefix="#"),
    ".conf": CommentStyle(line_prefix="#"),
    ".properties": CommentStyle(line_prefix="#"),
    
    # Block-comment languages
    ".rs": CommentStyle(line_prefix="//", block_start="/*", block_end="*/"),
    ".c": CommentStyle(line_prefix="//", block_start="/*", block_end="*/"),
    ".h": CommentStyle(line_prefix="//", block_start="/*", block_end="*/"),
    ".cpp": CommentStyle(line_prefix="//", block_start="/*", block_end="*/"),
    ".hpp": CommentStyle(line_prefix="//", block_start="/*", block_end="*/"),
    ".cc": CommentStyle(line_prefix="//", block_start="/*", block_end="*/"),
    ".cxx": CommentStyle(line_prefix="//", block_start="/*", block_end="*/"),
    ".java": CommentStyle(line_prefix="//", block_start="/*", block_end="*/"),
    ".kt": CommentStyle(line_prefix="//", block_start="/*", block_end="*/"),
    ".kts": CommentStyle(line_prefix="//", block_start="/*", block_end="*/"),
    ".scala": CommentStyle(line_prefix="//", block_start="/*", block_end="*/"),
    ".go": CommentStyle(line_prefix="//", block_start="/*", block_end="*/"),
    ".swift": CommentStyle(line_prefix="//", block_start="/*", block_end="*/"),
    ".js": CommentStyle(line_prefix="//", block_start="/*", block_end="*/"),
    ".mjs": CommentStyle(line_prefix="//", block_start="/*", block_end="*/"),
    ".ts": CommentStyle(line_prefix="//", block_start="/*", block_end="*/"),
    ".tsx": CommentStyle(line_prefix="//", block_start="/*", block_end="*/"),
    ".jsx": CommentStyle(line_prefix="//", block_start="/*", block_end="*/"),
    ".css": CommentStyle(line_prefix="", block_start="/*", block_end="*/"),
    ".scss": CommentStyle(line_prefix="//", block_start="/*", block_end="*/"),
    ".less": CommentStyle(line_prefix="//", block_start="/*", block_end="*/"),
    ".cs": CommentStyle(line_prefix="//", block_start="/*", block_end="*/"),
    ".fs": CommentStyle(line_prefix="//", block_start="(*", block_end="*)"),
    ".m": CommentStyle(line_prefix="//", block_start="/*", block_end="*/"),
    ".mm": CommentStyle(line_prefix="//", block_start="/*", block_end="*/"),
    ".proto": CommentStyle(line_prefix="//"),
    ".sql": CommentStyle(line_prefix="--"),
    ".lua": CommentStyle(line_prefix="--", block_start="--[[", block_end="]]"),
    
    # HTML/XML style
    ".html": CommentStyle(line_prefix="", block_start="<!--", block_end="-->"),
    ".htm": CommentStyle(line_prefix="", block_start="<!--", block_end="-->"),
    ".xml": CommentStyle(line_prefix="", block_start="<!--", block_end="-->"),
    ".xsl": CommentStyle(line_prefix="", block_start="<!--", block_end="-->"),
    ".xslt": CommentStyle(line_prefix="", block_start="<!--", block_end="-->"),
    ".svg": CommentStyle(line_prefix="", block_start="<!--", block_end="-->"),
    
    # Lisp-family
    ".lisp": CommentStyle(line_prefix=";;"),
    ".cl": CommentStyle(line_prefix=";;"),
    ".clj": CommentStyle(line_prefix=";;"),
    ".cljs": CommentStyle(line_prefix=";;"),
    ".el": CommentStyle(line_prefix=";;"),
    ".scm": CommentStyle(line_prefix=";;"),
    ".rkt": CommentStyle(line_prefix=";;"),
    
    # Other
    ".hs": CommentStyle(line_prefix="--", block_start="{-", block_end="-}"),
    ".erl": CommentStyle(line_prefix="%"),
    ".ex": CommentStyle(line_prefix="#"),
    ".exs": CommentStyle(line_prefix="#"),
    ".zig": CommentStyle(line_prefix="//"),
    ".nim": CommentStyle(line_prefix="#"),
    ".v": CommentStyle(line_prefix="//", block_start="/*", block_end="*/"),
    ".vhdl": CommentStyle(line_prefix="--"),
    ".vhd": CommentStyle(line_prefix="--"),
    ".tcl": CommentStyle(line_prefix="#"),
    ".cmake": CommentStyle(line_prefix="#"),
    ".gradle": CommentStyle(line_prefix="//", block_start="/*", block_end="*/"),
    ".groovy": CommentStyle(line_prefix="//", block_start="/*", block_end="*/"),
}

# Directories to always skip
SKIP_DIRECTORIES: set[str] = {
    ".git", ".svn", ".hg", ".bzr",
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    "node_modules", "bower_components",
    "venv", ".venv", "env", ".env",
    "build", "dist", "target", "out",
    ".idea", ".vscode", ".eclipse",
    "vendor", "third_party", "external",
    ".tox", ".nox",
    "eggs", "*.egg-info",
}

# Files to always skip
SKIP_FILES: set[str] = {
    "LICENSE", "LICENSE.txt", "LICENSE.md",
    "NOTICE", "NOTICE.txt",
    "COPYING", "COPYING.txt",
    ".gitignore", ".gitattributes",
    ".dockerignore", "Dockerfile",
    "Makefile", "CMakeLists.txt",
    "package.json", "package-lock.json",
    "Cargo.lock", "poetry.lock", "Pipfile.lock",
    "requirements.txt", "setup.cfg", "pyproject.toml",
}


# =============================================================================
# Core Logic
# =============================================================================

class LicenseToolError(Exception):
    """Base exception for license tool errors."""
    pass


class FileProcessingError(LicenseToolError):
    """Raised when a file cannot be processed."""
    def __init__(self, path: Path, reason: str):
        self.path = path
        self.reason = reason
        super().__init__(f"Failed to process {path}: {reason}")


@dataclass
class ProcessingResult:
    """Result of processing a single file."""
    path: Path
    action: str  # "created", "updated", "skipped", "error"
    message: str


def has_license_header(content: str) -> bool:
    """
    Check if file already contains an Apache 2.0 license header.
    
    Looks for key phrases that indicate Apache 2.0 licensing.
    """
    indicators = [
        "Apache License, Version 2.0",
        "Licensed under the Apache License",
        "http://www.apache.org/licenses/LICENSE-2.0",
    ]
    # Check first 2000 chars (headers should be at the top)
    header_region = content[:2000].lower()
    return any(indicator.lower() in header_region for indicator in indicators)


def extract_shebang(content: str) -> tuple[str | None, str]:
    """
    Extract shebang line from content if present.
    
    Returns:
        Tuple of (shebang_line or None, remaining_content)
    """
    if content.startswith("#!"):
        newline_idx = content.find("\n")
        if newline_idx != -1:
            return content[:newline_idx + 1], content[newline_idx + 1:]
        return content, ""
    return None, content


def add_header_to_content(
    content: str,
    style: CommentStyle,
    header_text: str
) -> str:
    """
    Add license header to file content, preserving shebang if needed.
    """
    shebang = None
    working_content = content
    
    if style.preserve_shebang:
        shebang, working_content = extract_shebang(content)
    
    formatted_header = style.format_header(header_text)
    
    # Build new content
    parts = []
    if shebang:
        parts.append(shebang.rstrip("\n"))
    parts.append(formatted_header)
    
    # Add blank line before existing content if it exists
    stripped_content = working_content.lstrip("\n")
    if stripped_content:
        parts.append("")  # Blank line separator
        parts.append(stripped_content)
    
    return "\n".join(parts)


def should_skip_path(path: Path) -> bool:
    """Check if a path should be skipped based on directory/file rules."""
    # Check directory components
    for part in path.parts:
        if part in SKIP_DIRECTORIES:
            return True
        # Handle glob patterns like *.egg-info
        for skip_pattern in SKIP_DIRECTORIES:
            if "*" in skip_pattern and path.match(skip_pattern):
                return True
    
    # Check filename
    if path.name in SKIP_FILES:
        return True
    
    return False


def process_file(
    file_path: Path,
    dry_run: bool = False,
    backup: bool = False
) -> ProcessingResult:
    """
    Process a single file, adding license header if needed.
    
    Args:
        file_path: Path to the file to process
        dry_run: If True, don't actually modify files
        backup: If True, create .bak backup before modifying
    
    Returns:
        ProcessingResult indicating what happened
    """
    suffix = file_path.suffix.lower()
    
    # Check if we support this file type
    if suffix not in COMMENT_STYLES:
        return ProcessingResult(
            file_path, "skipped", f"Unsupported file type: {suffix}"
        )
    
    # Check skip rules
    if should_skip_path(file_path):
        return ProcessingResult(file_path, "skipped", "In skip list")
    
    try:
        content = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return ProcessingResult(file_path, "skipped", "Binary or non-UTF-8 file")
    except PermissionError:
        return ProcessingResult(file_path, "error", "Permission denied")
    except OSError as e:
        return ProcessingResult(file_path, "error", str(e))
    
    # Check if already has header
    if has_license_header(content):
        return ProcessingResult(file_path, "skipped", "Already has license header")
    
    # Skip empty files
    if not content.strip():
        return ProcessingResult(file_path, "skipped", "Empty file")
    
    # Generate new content
    style = COMMENT_STYLES[suffix]
    new_content = add_header_to_content(content, style, LICENSE_HEADER_TEMPLATE)
    
    if dry_run:
        return ProcessingResult(file_path, "updated", "[DRY RUN] Would add header")
    
    # Create backup if requested
    if backup:
        backup_path = file_path.with_suffix(file_path.suffix + ".bak")
        try:
            shutil.copy2(file_path, backup_path)
        except OSError as e:
            return ProcessingResult(
                file_path, "error", f"Failed to create backup: {e}"
            )
    
    # Write updated content
    try:
        file_path.write_text(new_content, encoding="utf-8")
    except OSError as e:
        return ProcessingResult(file_path, "error", f"Failed to write: {e}")
    
    return ProcessingResult(file_path, "updated", "Added license header")


def create_notice_file(
    repo_root: Path,
    dry_run: bool = False
) -> ProcessingResult:
    """
    Create the NOTICE file required by Apache 2.0.
    """
    notice_path = repo_root / "NOTICE"
    
    if notice_path.exists():
        return ProcessingResult(notice_path, "skipped", "NOTICE file already exists")
    
    if dry_run:
        return ProcessingResult(
            notice_path, "created", "[DRY RUN] Would create NOTICE"
        )
    
    try:
        notice_path.write_text(NOTICE_CONTENT, encoding="utf-8")
    except OSError as e:
        return ProcessingResult(notice_path, "error", f"Failed to create: {e}")
    
    return ProcessingResult(notice_path, "created", "Created NOTICE file")


def find_source_files(repo_root: Path) -> list[Path]:
    """
    Recursively find all source files that might need headers.
    """
    source_files = []
    
    for path in repo_root.rglob("*"):
        if path.is_file() and not should_skip_path(path):
            if path.suffix.lower() in COMMENT_STYLES:
                source_files.append(path)
    
    return sorted(source_files)


def run_license_tool(
    repo_root: Path,
    dry_run: bool = False,
    backup: bool = False,
    verbose: bool = True
) -> dict[str, list[ProcessingResult]]:
    """
    Run the complete license tool on a repository.
    
    Args:
        repo_root: Root directory of the repository
        dry_run: If True, don't modify any files
        backup: If True, create .bak files before modifying
        verbose: If True, print progress information
    
    Returns:
        Dictionary mapping action types to lists of results
    """
    results: dict[str, list[ProcessingResult]] = {
        "created": [],
        "updated": [],
        "skipped": [],
        "error": [],
    }
    
    log: Callable[[str], None] = print if verbose else lambda _: None
    
    # Verify repo root exists
    if not repo_root.is_dir():
        raise LicenseToolError(f"Repository root not found: {repo_root}")
    
    mode_str = "[DRY RUN] " if dry_run else ""
    log(f"\n{mode_str}Processing repository: {repo_root}\n")
    log("=" * 60)
    
    # Step 1: Create NOTICE file
    log("\n[1/2] Checking NOTICE file...")
    notice_result = create_notice_file(repo_root, dry_run)
    results[notice_result.action].append(notice_result)
    log(f"  {notice_result.action.upper()}: {notice_result.message}")
    
    # Step 2: Process source files
    log("\n[2/2] Processing source files...")
    source_files = find_source_files(repo_root)
    log(f"  Found {len(source_files)} candidate files\n")
    
    for file_path in source_files:
        result = process_file(file_path, dry_run, backup)
        results[result.action].append(result)
        
        # Only log non-skipped files in verbose mode
        if result.action != "skipped" or verbose:
            rel_path = file_path.relative_to(repo_root)
            symbol = {
                "created": "+",
                "updated": "✓",
                "skipped": "-",
                "error": "✗",
            }.get(result.action, "?")
            log(f"  [{symbol}] {rel_path}: {result.message}")
    
    # Summary
    log("\n" + "=" * 60)
    log("SUMMARY:")
    log(f"  Created: {len(results['created'])}")
    log(f"  Updated: {len(results['updated'])}")
    log(f"  Skipped: {len(results['skipped'])}")
    log(f"  Errors:  {len(results['error'])}")
    log("=" * 60 + "\n")
    
    return results


# =============================================================================
# CLI Entry Point
# =============================================================================

def main() -> int:
    """Main entry point for CLI usage."""
    parser = argparse.ArgumentParser(
        description="Apache 2.0 License Management Tool for Symbo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/repo              # Add headers to all files
  %(prog)s /path/to/repo --dry-run    # Preview changes without modifying
  %(prog)s /path/to/repo --backup     # Create .bak files before modifying
  %(prog)s . --quiet                  # Process current directory quietly
        """,
    )
    
    parser.add_argument(
        "repo_root",
        type=Path,
        help="Root directory of the repository to process",
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument(
        "--backup", "-b",
        action="store_true",
        help="Create .bak backup files before modifying",
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress progress output (still shows summary)",
    )
    
    args = parser.parse_args()
    
    try:
        results = run_license_tool(
            repo_root=args.repo_root.resolve(),
            dry_run=args.dry_run,
            backup=args.backup,
            verbose=not args.quiet,
        )
        
        # Return non-zero if there were errors
        return 1 if results["error"] else 0
        
    except LicenseToolError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
