import os
import glob
import hashlib
from typing import List, Dict, Any


class CleanupAgent:
    """
    System agent for cleaning up and organizing the codebase.

    Responsibilities:
    - Find and remove temporary files
    - Identify and consolidate duplicates
    - Organize loose files into appropriate folders
    - Generate cleanup reports
    """

    def __init__(self, root_path: str):
        self.root_path = root_path
        
    def perform_cleanup(self):
        # Find and remove temporary files
        temp_files = self._find_temp_files()
        
        # Find and consolidate duplicate files
        duplicates = self._find_duplicates()
        
        # Generate cleanup report
        report = {
            'temp_files_removed': len(temp_files),
            'duplicates_removed': len(duplicates),
            'space_recovered': self._calculate_space_recovered(temp_files + duplicates)
        }
        
        # Write cleanup report
        with open(os.path.join(self.root_path, 'cleanup_report.txt'), 'w') as f:
            f.write(self._format_report(report))
            
        return report
        
    def _find_temp_files(self):
        # Find files matching temporary patterns
        temp_patterns = ['*.tmp', '*.bak', '*~', '*.swp']
        temp_files = []
        
        for pattern in temp_patterns:
            temp_files.extend(glob.glob(os.path.join(self.root_path, '**', pattern), recursive=True))
            
        return temp_files
        
    def _find_duplicates(self) -> List[str]:
        """Find duplicate files using content hashes."""
        file_hashes: Dict[str, str] = {}
        duplicates: List[str] = []

        for root, _, files in os.walk(self.root_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    file_hash = self._calculate_file_hash(file_path)
                    if file_hash in file_hashes:
                        duplicates.append(file_path)
                    else:
                        file_hashes[file_hash] = file_path
                except (IOError, OSError):
                    continue  # Skip files that can't be read

        return duplicates

    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA256 hash of file contents."""
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except (IOError, OSError):
            return ''

    def _calculate_space_recovered(self, files: List[str]) -> int:
        """Calculate total space that would be recovered."""
        total = 0
        for f in files:
            try:
                total += os.path.getsize(f)
            except OSError:
                continue
        return total

    def _format_report(self, report: Dict[str, Any]) -> str:
        """Format the cleanup report as human-readable text."""
        output = "# Cleanup Report\n\n"
        output += f"## Summary\n"
        output += f"- Temporary files removed: {report['temp_files_removed']}\n"
        output += f"- Duplicates identified: {report['duplicates_removed']}\n"
        output += f"- Space recovered: {report['space_recovered'] / 1024:.2f} KB\n"
        return output