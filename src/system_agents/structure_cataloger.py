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
Structure Cataloger Agent for Symbo Mathematical Multi-Agentic Reasoning System.

Dynamically scans and catalogs the entire codebase structure, identifying:
- Agent hierarchies (supervisors, specialists, infrastructure)
- Module dependencies
- Class and function inventories
- Architecture patterns
"""

import os
import ast
import re
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class ModuleInfo:
    """Information about a Python module."""
    path: str
    name: str
    line_count: int
    classes: List[str] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    docstring: Optional[str] = None


@dataclass
class AgentInfo:
    """Information about an agent in the system."""
    name: str
    path: str
    agent_type: str  # supervisor, specialist, infrastructure, system
    domain: Optional[str] = None
    capabilities: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)


class StructureCataloger:
    """
    Dynamic structure cataloger that scans and documents the Symbo codebase.

    Responsibilities:
    - Scan all Python modules and extract metadata
    - Identify agent hierarchy and relationships
    - Map dependencies between modules
    - Generate comprehensive catalogs
    """

    def __init__(self, root_path: str):
        self.root_path = root_path
        self.modules: Dict[str, ModuleInfo] = {}
        self.agents: Dict[str, AgentInfo] = {}
        self.dependency_graph: Dict[str, Set[str]] = defaultdict(set)

    def scan_codebase(self) -> Dict[str, Any]:
        """Perform full codebase scan."""
        self._scan_python_files()
        self._identify_agents()
        self._build_dependency_graph()

        return {
            'modules': self.modules,
            'agents': self.agents,
            'dependencies': dict(self.dependency_graph)
        }

    def _scan_python_files(self):
        """Scan all Python files in the codebase."""
        for root, dirs, files in os.walk(self.root_path):
            # Skip common non-source directories
            dirs[:] = [d for d in dirs if d not in {
                '__pycache__', '.git', 'node_modules', '.venv', 'venv',
                'build', 'dist', '.egg-info', '.tox', '.pytest_cache'
            }]

            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    module_info = self._analyze_module(file_path)
                    if module_info:
                        rel_path = os.path.relpath(file_path, self.root_path)
                        self.modules[rel_path] = module_info

    def _analyze_module(self, file_path: str) -> Optional[ModuleInfo]:
        """Analyze a single Python module."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            lines = content.split('\n')
            line_count = len(lines)

            # Parse AST for detailed analysis
            try:
                tree = ast.parse(content)
                classes = [node.name for node in ast.walk(tree)
                          if isinstance(node, ast.ClassDef)]
                functions = [node.name for node in ast.walk(tree)
                            if isinstance(node, ast.FunctionDef)
                            and not node.name.startswith('_')]

                # Extract docstring
                docstring = ast.get_docstring(tree)

                # Extract imports
                imports = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        module = node.module or ''
                        imports.append(module)

            except SyntaxError:
                # Fallback to regex-based extraction
                classes = re.findall(r'^class\s+(\w+)', content, re.MULTILINE)
                functions = re.findall(r'^def\s+(\w+)', content, re.MULTILINE)
                imports = re.findall(r'^(?:from\s+(\S+)|import\s+(\S+))',
                                    content, re.MULTILINE)
                imports = [i[0] or i[1] for i in imports]
                docstring = None

            return ModuleInfo(
                path=file_path,
                name=os.path.basename(file_path),
                line_count=line_count,
                classes=classes,
                functions=functions,
                imports=imports,
                docstring=docstring
            )

        except Exception as e:
            return None

    def _identify_agents(self):
        """Identify and categorize all agents in the codebase."""
        agent_patterns = {
            'supervisor': ['supervisor', 'orchestrator', 'coordinator'],
            'specialist': ['specialist', 'solver', 'calculator', 'analyzer'],
            'infrastructure': ['pool', 'facilitator', 'management', 'registry'],
            'system': ['cataloger', 'audit', 'cleanup', 'crackfinder', 'documentation']
        }

        for rel_path, module in self.modules.items():
            # Check if module contains agent-like classes
            for class_name in module.classes:
                class_lower = class_name.lower()
                module_lower = module.name.lower()

                # Determine agent type
                agent_type = None
                for atype, patterns in agent_patterns.items():
                    if any(p in class_lower or p in module_lower for p in patterns):
                        agent_type = atype
                        break

                # Also check for BDI agents
                if 'agent' in class_lower or 'bdi' in class_lower:
                    agent_type = agent_type or 'specialist'

                if agent_type:
                    # Extract domain from path
                    domain = self._extract_domain(rel_path)

                    self.agents[class_name] = AgentInfo(
                        name=class_name,
                        path=rel_path,
                        agent_type=agent_type,
                        domain=domain,
                        capabilities=self._extract_capabilities(module),
                        dependencies=module.imports[:10]  # Top 10 imports
                    )

    def _extract_domain(self, path: str) -> Optional[str]:
        """Extract mathematical domain from file path."""
        domains = ['algebra', 'calculus', 'linear_algebra', 'linalg',
                   'statistics', 'stats', 'geometry', 'discrete',
                   'number_theory', 'optimization', 'physics']

        path_lower = path.lower()
        for domain in domains:
            if domain in path_lower:
                return domain.replace('_', ' ').title()
        return None

    def _extract_capabilities(self, module: ModuleInfo) -> List[str]:
        """Extract capabilities from module's public functions."""
        return [f for f in module.functions
                if not f.startswith('_') and len(f) > 3][:10]

    def _build_dependency_graph(self):
        """Build graph of inter-module dependencies."""
        module_names = {m.name.replace('.py', '') for m in self.modules.values()}

        for rel_path, module in self.modules.items():
            for imp in module.imports:
                # Check if import refers to internal module
                imp_base = imp.split('.')[-1]
                if imp_base in module_names:
                    self.dependency_graph[rel_path].add(imp_base)

    def generate_catalog(self, output_path: str) -> str:
        """Generate comprehensive catalog document."""
        if not self.modules:
            self.scan_codebase()

        catalog = self._format_catalog()

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(catalog)

        return catalog

    def _format_catalog(self) -> str:
        """Format the catalog as markdown."""
        output = ['# Symbo System Structure Catalog\n']
        output.append('## System Overview\n')
        output.append('Symbo Mathematical Multi-Agentic Reasoning System\n\n')
        output.append('## Architecture\n')
        output.append('Hierarchical Hub-and-Spoke architecture with supervisor agents coordinating specialists\n\n')

        # Statistics
        output.append('## Statistics\n')
        total_lines = sum(m.line_count for m in self.modules.values())
        total_classes = sum(len(m.classes) for m in self.modules.values())
        total_functions = sum(len(m.functions) for m in self.modules.values())
        output.append(f'- Total Python files: {len(self.modules)}\n')
        output.append(f'- Total lines of code: {total_lines:,}\n')
        output.append(f'- Total classes: {total_classes}\n')
        output.append(f'- Total functions: {total_functions}\n\n')

        # Agent hierarchy
        output.append('## Agent Hierarchy\n')
        for agent_type in ['supervisor', 'specialist', 'infrastructure', 'system']:
            agents = [a for a in self.agents.values() if a.agent_type == agent_type]
            if agents:
                output.append(f'### {agent_type.title()} Agents ({len(agents)})\n')
                for agent in agents:
                    output.append(f'- **{agent.name}** ({agent.path})\n')
                    if agent.domain:
                        output.append(f'  - Domain: {agent.domain}\n')
                    if agent.capabilities:
                        output.append(f'  - Capabilities: {", ".join(agent.capabilities[:5])}\n')
                output.append('\n')

        # Large modules (candidates for decomposition)
        output.append('## Large Modules (>300 lines)\n')
        large_modules = [(p, m) for p, m in self.modules.items() if m.line_count > 300]
        large_modules.sort(key=lambda x: x[1].line_count, reverse=True)
        for path, module in large_modules[:20]:
            output.append(f'- **{path}**: {module.line_count} lines, ')
            output.append(f'{len(module.classes)} classes, {len(module.functions)} functions\n')
        output.append('\n')

        # Module by directory
        output.append('## Modules by Directory\n')
        by_dir = defaultdict(list)
        for path, module in self.modules.items():
            dir_name = os.path.dirname(path) or 'root'
            by_dir[dir_name].append((path, module))

        for dir_name in sorted(by_dir.keys()):
            modules = by_dir[dir_name]
            total = sum(m.line_count for _, m in modules)
            output.append(f'### {dir_name}/ ({len(modules)} files, {total:,} lines)\n')
            for path, module in sorted(modules, key=lambda x: x[1].line_count, reverse=True)[:10]:
                output.append(f'- {module.name}: {module.line_count} lines\n')
            if len(modules) > 10:
                output.append(f'- ... and {len(modules) - 10} more\n')
            output.append('\n')

        return ''.join(output)

    def _document_specializations(self) -> Dict[str, List[str]]:
        """Document agent specializations."""
        specializations = {}
        for name, agent in self.agents.items():
            specializations[name] = agent.capabilities
        return specializations

    def _map_agent_interactions(self) -> Dict[str, List[str]]:
        """Map interactions between agents based on imports."""
        interactions = {}
        agent_modules = {a.path: a.name for a in self.agents.values()}

        for name, agent in self.agents.items():
            module = self.modules.get(agent.path)
            if module:
                interacts_with = []
                for imp in module.imports:
                    for path, aname in agent_modules.items():
                        if imp in path and aname != name:
                            interacts_with.append(aname)
                interactions[name] = list(set(interacts_with))

        return interactions


def main():
    """Run the structure cataloger."""
    import sys

    root = sys.argv[1] if len(sys.argv) > 1 else '.'
    cataloger = StructureCataloger(root)
    cataloger.scan_codebase()
    catalog = cataloger.generate_catalog('system_structure_catalog.md')
    print(catalog)


if __name__ == '__main__':
    main()
