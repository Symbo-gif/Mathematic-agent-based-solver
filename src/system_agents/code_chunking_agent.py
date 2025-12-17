from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import os
import re

class CodeChunkingAgent:
    def __init__(self, chunk_size=100, chunk_overlap=15):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Python-specific separators in order of preference
        self.separators = [
            '\n\n\n',  # Triple newlines (module-level separation)
            '\n\n',    # Double newlines (function/class separation)
            '\n',      # Single newline
            ' ',        # Space
            ''          # Character level
        ]
        
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=self.separators,
            length_function=self.count_lines
        )
    
    def count_lines(self, text):
        return len(text.split('\n'))
    
    def chunk_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract module-level imports to preserve in each chunk
        imports = self._extract_imports(content)
        
        # Split the code into logical chunks
        chunks = self.splitter.split_text(content)
        
        # Process each chunk
        processed_chunks = []
        for i, chunk in enumerate(chunks):
            # Add imports to each chunk for context
            chunk_with_imports = imports + '\n\n' + chunk
            processed_chunks.append({
                'content': chunk_with_imports,
                'metadata': {
                    'original_file': file_path,
                    'chunk_index': i,
                    'total_chunks': len(chunks)
                }
            })
        
        return processed_chunks
    
    def _extract_imports(self, code):
        # Extract module-level imports
        import_pattern = r'^(import \w+|from \w+ import [^\n]+)'
        imports = []
        for line in code.split('\n'):
            if re.match(import_pattern, line):
                imports.append(line)
            elif line.strip() and not line.startswith('#'):
                break  # Stop at first non-import code
        return '\n'.join(imports)
    
    def chunk_directory(self, directory_path, output_base='chunked'):
        all_chunks = {}
        
        for root, _, files in os.walk(directory_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, directory_path)
                    
                    print(f'Chunking: {relative_path}')
                    chunks = self.chunk_file(file_path)
                    all_chunks[relative_path] = chunks
        
        return all_chunks