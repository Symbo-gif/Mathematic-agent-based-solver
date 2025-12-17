import os
import re
from typing import Dict, List, Tuple


class DocumentationAgent:
    def __init__(self):
        self.function_pattern = re.compile(r'def\s+(\w+)\s*\(([^)]*)\)')
        self.class_pattern = re.compile(r'class\s+(\w+)\s*(?:\(|:)')
    
    def analyze_chunk(self, chunk_content: str) -> Dict:
        """Analyze a code chunk to identify functions and classes"""
        functions = []
        classes = []
        
        # Find all functions
        for match in self.function_pattern.finditer(chunk_content):
            func_name, params = match.groups()
            functions.append({
                'name': func_name,
                'parameters': params,
                'signature': f'def {func_name}({params})'
            })
        
        # Find all classes
        for match in self.class_pattern.finditer(chunk_content):
            class_name = match.group(1)
            classes.append({
                'name': class_name,
                'signature': f'class {class_name}'
            })
        
        return {
            'functions': functions,
            'classes': classes,
            'function_count': len(functions),
            'class_count': len(classes)
        }
    
    def generate_chunk_readme(self, chunk_metadata: Dict, analysis: Dict) -> str:
        """Generate README content for a chunk"""
        readme = f"""# {os.path.basename(chunk_metadata['original_file'])} - Chunk #{chunk_metadata['chunk_index']+1}

## Overview
This chunk contains part of `{os.path.basename(chunk_metadata['original_file'])}`.
It represents chunk {chunk_metadata['chunk_index']+1} of {chunk_metadata['total_chunks']} total chunks.

"""

        if analysis['function_count'] > 0:
            readme += "## Functions\n\n"
            for func in analysis['functions']:
                readme += f"- `{func['signature']}`\n"

        if analysis['class_count'] > 0:
            readme += "\n## Classes\n\n"
            for cls in analysis['classes']:
                readme += f"- `{cls['signature']}`\n"

        return readme
    
    def generate_directory_readme(self, directory_path: str, chunk_data: Dict):
        """Generate overall directory README showing chunk structure"""
        readme = f"""# Codebase Chunk Structure

This directory contains the chunked version of the original codebase.

## Chunked Files

"""

        for file_path, chunks in chunk_data.items():
            readme += f"### {file_path} ({len(chunks)} chunks)\n\n"
            
            # Show first chunk's contents as example
            if chunks:
                analysis = self.analyze_chunk(chunks[0]['content'])
                if analysis['function_count'] > 0:
                    readme += "Functions in first chunk:\n"
                    for func in analysis['functions'][:3]:  # Show up to 3 functions
                        readme += f"- {func['name']}\n"
                    if analysis['function_count'] > 3:
                        readme += f"- ... and {analysis['function_count']-3} more\n"
                
                readme += "\n"

        return readme