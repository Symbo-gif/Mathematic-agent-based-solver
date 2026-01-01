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

import ast
import os
import re
import sys
from typing import List, Dict, Any

class StaticAuditor:
    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        self.findings = {
            "missing_implementations": [],
            "todos": [],
            "mocks": [],
            "hardcoded_data": []
        }

    def scan(self):
        for root, dirs, files in os.walk(self.root_dir):
            if "audit" in root or "tests" in root or "__pycache__" in root:
                continue
            
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    self.analyze_file(file_path)

    def analyze_file(self, file_path: str):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # String-based checks
            self.check_todos(file_path, content)
            self.check_mocks(file_path, content)
            
            # AST-based checks
            tree = ast.parse(content)
            self.check_ast(file_path, tree)
            
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")

    def check_todos(self, file_path: str, content: str):
        lines = content.splitlines()
        for i, line in enumerate(lines):
            if "TODO" in line or "FIXME" in line:
                self.findings["todos"].append({
                    "file": file_path,
                    "line": i + 1,
                    "content": line.strip()
                })

    def check_mocks(self, file_path: str, content: str):
        if "unittest.mock" in content or "pytest_mock" in content:
             self.findings["mocks"].append({
                "file": file_path,
                "message": "Potential mock usage detected via import string"
            })

    def check_ast(self, file_path: str, tree: ast.AST):
        # Whitelist for hardcoded data
        if any(x in file_path for x in ["sandbox_evaluator.py", "omdoc_schema.py", "synthetic_data_generator.py", "__init__.py"]):
             pass # Skip hardcoded data check for known config/schema files
        else:
             for node in ast.walk(tree):
                # Check for hardcoded lists/dicts (heuristic: large containers)
                if isinstance(node, (ast.List, ast.Dict)):
                    # This is a weak heuristic, but let's flag very large literals
                    if len(node.keys if isinstance(node, ast.Dict) else node.elts) > 20:
                         self.findings["hardcoded_data"].append({
                            "file": file_path,
                            "line": node.lineno,
                            "message": "Potential large hardcoded data structure detected"
                        })

        for node in ast.walk(tree):
            # Check for empty functions or functions with only 'pass'
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if self.is_empty_or_pass(node):
                    # Check for @abstractmethod decorator
                    is_abstract = False
                    for decorator in node.decorator_list:
                        if isinstance(decorator, ast.Name) and decorator.id == 'abstractmethod':
                            is_abstract = True
                        elif isinstance(decorator, ast.Attribute) and decorator.attr == 'abstractmethod':
                            is_abstract = True
                    
                    if not is_abstract:
                        self.findings["missing_implementations"].append({
                            "file": file_path,
                            "line": node.lineno,
                            "function": node.name,
                            "message": "Function implementation missing (pass or empty)"
                        })

    def is_empty_or_pass(self, node):
        if not node.body:
            return True
        
        has_docstring = False
        relevant_body = []
        for stmt in node.body:
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, str):
                has_docstring = True
                continue # Skip docstrings
            relevant_body.append(stmt)
        
        if has_docstring:
            return False # If it has a docstring, assume it's documented intent (hook/interface)
        
        if not relevant_body:
            return True # Empty and no docstring
        
        if len(relevant_body) == 1 and isinstance(relevant_body[0], ast.Pass):
            return True
            
        return False

    def report(self):
        print("="*80)
        print("STATIC ANALYSIS REPORT")
        print("="*80)
        
        for category, items in self.findings.items():
            print(f"\n[{category.upper()}] - {len(items)} findings")
            for item in items[:10]: # Limit output
                print(f"  - {item}")
            if len(items) > 10:
                print(f"  ... and {len(items) - 10} more")

if __name__ == "__main__":
    root = os.getcwd()
    auditor = StaticAuditor(root)
    auditor.scan()
    auditor.report()
