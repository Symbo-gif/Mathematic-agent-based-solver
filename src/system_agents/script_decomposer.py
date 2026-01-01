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
Script Decomposer Agent for Symbo Mathematical Multi-Agentic Reasoning System.

Analyzes large, monolithic scripts and decomposes them into
supervisor-specialist agent team structures following the LangChain
supervisor pattern.

Key Patterns Applied:
1. Supervisor agents that route to specialists
2. Tool wrapping for sub-agents
3. Human-in-the-loop middleware integration points
4. Layered architecture: API tools → Sub-agents → Supervisor
"""

import os
import ast
import re
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from collections import defaultdict
from enum import Enum


class ComponentType(Enum):
    """Types of components identified in decomposition."""
    SUPERVISOR = "supervisor"
    SPECIALIST = "specialist"
    UTILITY = "utility"
    DATA_MODEL = "data_model"
    MIDDLEWARE = "middleware"


@dataclass
class FunctionInfo:
    """Information about a function for decomposition analysis."""
    name: str
    line_start: int
    line_end: int
    args: List[str]
    returns: Optional[str]
    docstring: Optional[str]
    calls: List[str]  # Functions this function calls
    complexity: int  # Cyclomatic complexity estimate
    domain: Optional[str] = None


@dataclass
class ClassInfo:
    """Information about a class for decomposition analysis."""
    name: str
    line_start: int
    line_end: int
    methods: List[FunctionInfo]
    bases: List[str]
    docstring: Optional[str]
    responsibilities: List[str] = field(default_factory=list)
    suggested_type: ComponentType = ComponentType.UTILITY


@dataclass
class DecompositionPlan:
    """Plan for decomposing a monolithic script."""
    original_file: str
    total_lines: int
    components: List[Dict[str, Any]]
    supervisor_spec: Dict[str, Any]
    specialist_specs: List[Dict[str, Any]]
    shared_utilities: List[str]
    migration_steps: List[str]


class ScriptDecomposer:
    """
    Analyzes and decomposes large scripts into agent team structures.

    Process:
    1. Parse and analyze the script's AST
    2. Identify responsibilities and domains
    3. Group related functionality
    4. Design supervisor-specialist structure
    5. Generate migration plan
    """

    # Domain keywords for classification
    DOMAIN_KEYWORDS = {
        'algebra': ['polynomial', 'equation', 'factor', 'solve', 'root', 'quadratic'],
        'calculus': ['derivative', 'integral', 'limit', 'diff', 'integrate', 'taylor'],
        'linear_algebra': ['matrix', 'vector', 'eigenvalue', 'determinant', 'svd', 'decomposition'],
        'statistics': ['probability', 'distribution', 'mean', 'variance', 'regression', 'bayesian'],
        'geometry': ['point', 'line', 'circle', 'angle', 'triangle', 'polygon'],
        'number_theory': ['prime', 'gcd', 'modular', 'congruence', 'divisor'],
        'optimization': ['minimize', 'maximize', 'gradient', 'constraint', 'objective'],
    }

    # Keywords indicating supervisor responsibility
    SUPERVISOR_KEYWORDS = ['route', 'dispatch', 'delegate', 'coordinate', 'orchestrate',
                          'process', 'handle', 'manage', 'analyze_task']

    def __init__(self):
        self.functions: Dict[str, FunctionInfo] = {}
        self.classes: Dict[str, ClassInfo] = {}
        self.imports: List[str] = []
        self.call_graph: Dict[str, Set[str]] = defaultdict(set)

    def analyze_file(self, file_path: str) -> DecompositionPlan:
        """Analyze a Python file and create a decomposition plan."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        lines = content.split('\n')
        total_lines = len(lines)

        # Parse AST
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            return DecompositionPlan(
                original_file=file_path,
                total_lines=total_lines,
                components=[],
                supervisor_spec={'error': str(e)},
                specialist_specs=[],
                shared_utilities=[],
                migration_steps=[f"Fix syntax error: {e}"]
            )

        # Extract information
        self._extract_imports(tree)
        self._extract_functions(tree)
        self._extract_classes(tree)
        self._build_call_graph(tree)
        self._classify_components()

        # Generate decomposition plan
        return self._generate_plan(file_path, total_lines)

    def _extract_imports(self, tree: ast.AST):
        """Extract import statements."""
        self.imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.imports.append(f"import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                names = ', '.join(alias.name for alias in node.names)
                self.imports.append(f"from {module} import {names}")

    def _extract_functions(self, tree: ast.AST):
        """Extract function information from AST."""
        self.functions = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Skip methods (they're handled in class extraction)
                if not self._is_method(node, tree):
                    func_info = self._analyze_function(node)
                    self.functions[node.name] = func_info

    def _extract_classes(self, tree: ast.AST):
        """Extract class information from AST."""
        self.classes = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_info = self._analyze_class(node)
                self.classes[node.name] = class_info

    def _is_method(self, func_node: ast.FunctionDef, tree: ast.AST) -> bool:
        """Check if a function is a method inside a class."""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for item in node.body:
                    if item is func_node:
                        return True
        return False

    def _analyze_function(self, node: ast.FunctionDef) -> FunctionInfo:
        """Analyze a function node."""
        # Extract arguments
        args = [arg.arg for arg in node.args.args]

        # Extract return annotation if present
        returns = None
        if node.returns:
            returns = ast.unparse(node.returns) if hasattr(ast, 'unparse') else str(node.returns)

        # Extract docstring
        docstring = ast.get_docstring(node)

        # Extract function calls
        calls = []
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    calls.append(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    calls.append(child.func.attr)

        # Estimate complexity (simplified cyclomatic complexity)
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler,
                                  ast.With, ast.Assert, ast.comprehension)):
                complexity += 1

        # Determine domain
        domain = self._identify_domain(node.name, docstring, calls)

        return FunctionInfo(
            name=node.name,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            args=args,
            returns=returns,
            docstring=docstring,
            calls=list(set(calls)),
            complexity=complexity,
            domain=domain
        )

    def _analyze_class(self, node: ast.ClassDef) -> ClassInfo:
        """Analyze a class node."""
        # Extract base classes
        bases = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
            elif isinstance(base, ast.Attribute):
                bases.append(base.attr)

        # Extract docstring
        docstring = ast.get_docstring(node)

        # Extract methods
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods.append(self._analyze_function(item))

        # Identify responsibilities from method names and docstrings
        responsibilities = self._identify_responsibilities(node.name, methods, docstring)

        return ClassInfo(
            name=node.name,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            methods=methods,
            bases=bases,
            docstring=docstring,
            responsibilities=responsibilities
        )

    def _identify_domain(self, name: str, docstring: Optional[str],
                        calls: List[str]) -> Optional[str]:
        """Identify the mathematical domain of a function."""
        text = f"{name} {docstring or ''} {' '.join(calls)}".lower()

        domain_scores = {}
        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > 0:
                domain_scores[domain] = score

        if domain_scores:
            return max(domain_scores, key=domain_scores.get)
        return None

    def _identify_responsibilities(self, class_name: str,
                                  methods: List[FunctionInfo],
                                  docstring: Optional[str]) -> List[str]:
        """Identify class responsibilities from methods."""
        responsibilities = []

        method_names = [m.name for m in methods if not m.name.startswith('_')]

        # Check for common responsibility patterns
        if any('solve' in m.lower() for m in method_names):
            responsibilities.append('Problem solving')
        if any('parse' in m.lower() for m in method_names):
            responsibilities.append('Input parsing')
        if any('validate' in m.lower() or 'verify' in m.lower() for m in method_names):
            responsibilities.append('Validation/Verification')
        if any('format' in m.lower() or 'render' in m.lower() for m in method_names):
            responsibilities.append('Output formatting')
        if any('route' in m.lower() or 'dispatch' in m.lower() for m in method_names):
            responsibilities.append('Task routing')
        if any('process' in m.lower() for m in method_names):
            responsibilities.append('Processing')

        return responsibilities

    def _build_call_graph(self, tree: ast.AST):
        """Build a graph of function calls."""
        self.call_graph = defaultdict(set)

        for func_name, func_info in self.functions.items():
            for call in func_info.calls:
                if call in self.functions:
                    self.call_graph[func_name].add(call)

        for class_info in self.classes.values():
            for method in class_info.methods:
                for call in method.calls:
                    self.call_graph[f"{class_info.name}.{method.name}"].add(call)

    def _classify_components(self):
        """Classify components as supervisor, specialist, utility, etc."""
        for class_name, class_info in self.classes.items():
            name_lower = class_name.lower()
            method_names = [m.name.lower() for m in class_info.methods]

            # Check for supervisor patterns
            if any(kw in name_lower for kw in ['supervisor', 'orchestrator', 'coordinator']):
                class_info.suggested_type = ComponentType.SUPERVISOR
            elif any(kw in name_lower or kw in ' '.join(method_names)
                    for kw in self.SUPERVISOR_KEYWORDS):
                class_info.suggested_type = ComponentType.SUPERVISOR
            # Check for specialist patterns
            elif any(kw in name_lower for kw in ['specialist', 'solver', 'handler', 'processor']):
                class_info.suggested_type = ComponentType.SPECIALIST
            # Check for data model patterns
            elif any(kw in name_lower for kw in ['model', 'entity', 'data', 'result', 'entry']):
                class_info.suggested_type = ComponentType.DATA_MODEL
            # Check for middleware patterns
            elif any(kw in name_lower for kw in ['middleware', 'interceptor', 'hook']):
                class_info.suggested_type = ComponentType.MIDDLEWARE
            # Default to utility
            else:
                class_info.suggested_type = ComponentType.UTILITY

    def _generate_plan(self, file_path: str, total_lines: int) -> DecompositionPlan:
        """Generate a decomposition plan."""
        components = []
        supervisor_spec = {}
        specialist_specs = []
        shared_utilities = []
        migration_steps = []

        # Identify supervisor candidates
        supervisors = [c for c in self.classes.values()
                       if c.suggested_type == ComponentType.SUPERVISOR]

        # Identify specialist candidates
        specialists = [c for c in self.classes.values()
                      if c.suggested_type == ComponentType.SPECIALIST]

        # If no clear supervisor, suggest creating one
        if not supervisors and len(specialists) > 1:
            supervisor_spec = {
                'name': f"{os.path.basename(file_path).replace('.py', '')}Supervisor",
                'create_new': True,
                'responsibilities': ['Route tasks to appropriate specialists',
                                   'Coordinate multi-step operations',
                                   'Aggregate results from specialists'],
                'specialist_tools': [s.name for s in specialists]
            }
            migration_steps.append(
                f"Create new supervisor agent: {supervisor_spec['name']}"
            )
        elif supervisors:
            sup = supervisors[0]
            supervisor_spec = {
                'name': sup.name,
                'create_new': False,
                'file': file_path,
                'lines': f"{sup.line_start}-{sup.line_end}",
                'responsibilities': sup.responsibilities
            }

        # Create specialist specifications
        for spec in specialists:
            domains = set()
            for method in spec.methods:
                if method.domain:
                    domains.add(method.domain)

            specialist_specs.append({
                'name': spec.name,
                'file': file_path,
                'lines': f"{spec.line_start}-{spec.line_end}",
                'domains': list(domains),
                'responsibilities': spec.responsibilities,
                'method_count': len(spec.methods),
                'suggested_extraction': len(spec.methods) > 10 or
                                       (spec.line_end - spec.line_start) > 200
            })

        # Identify shared utilities
        utilities = [c for c in self.classes.values()
                    if c.suggested_type in [ComponentType.UTILITY, ComponentType.DATA_MODEL]]
        shared_utilities = [u.name for u in utilities]

        # Generate migration steps
        migration_steps.extend([
            f"1. Extract data models to shared module: {', '.join(shared_utilities[:5])}",
            f"2. Create specialist agent files for: {', '.join(s['name'] for s in specialist_specs[:5])}",
            f"3. Implement supervisor with tool wrappers for each specialist",
            f"4. Add human-in-the-loop middleware for critical operations",
            f"5. Update imports and test integration",
        ])

        # Build component summary
        for cls in self.classes.values():
            components.append({
                'name': cls.name,
                'type': cls.suggested_type.value,
                'lines': cls.line_end - cls.line_start,
                'methods': len(cls.methods),
                'responsibilities': cls.responsibilities
            })

        return DecompositionPlan(
            original_file=file_path,
            total_lines=total_lines,
            components=components,
            supervisor_spec=supervisor_spec,
            specialist_specs=specialist_specs,
            shared_utilities=shared_utilities,
            migration_steps=migration_steps
        )

    def generate_report(self, plan: DecompositionPlan) -> str:
        """Generate a human-readable decomposition report."""
        report = [f"# Decomposition Plan: {os.path.basename(plan.original_file)}\n"]
        report.append(f"**Total Lines:** {plan.total_lines}\n")
        report.append(f"**Components Identified:** {len(plan.components)}\n\n")

        # Supervisor
        report.append("## Supervisor Agent\n")
        if plan.supervisor_spec:
            if plan.supervisor_spec.get('create_new'):
                report.append(f"**Recommended:** Create new supervisor `{plan.supervisor_spec['name']}`\n")
            else:
                report.append(f"**Existing:** `{plan.supervisor_spec['name']}`\n")
            if plan.supervisor_spec.get('responsibilities'):
                report.append("**Responsibilities:**\n")
                for resp in plan.supervisor_spec['responsibilities']:
                    report.append(f"- {resp}\n")
        report.append("\n")

        # Specialists
        report.append("## Specialist Agents\n")
        for spec in plan.specialist_specs:
            report.append(f"### {spec['name']}\n")
            report.append(f"- **Location:** Lines {spec['lines']}\n")
            report.append(f"- **Methods:** {spec['method_count']}\n")
            if spec['domains']:
                report.append(f"- **Domains:** {', '.join(spec['domains'])}\n")
            if spec['suggested_extraction']:
                report.append("- **⚠️ Recommended for extraction** (large component)\n")
            report.append("\n")

        # Shared utilities
        if plan.shared_utilities:
            report.append("## Shared Utilities\n")
            for util in plan.shared_utilities:
                report.append(f"- {util}\n")
            report.append("\n")

        # Migration steps
        report.append("## Migration Steps\n")
        for step in plan.migration_steps:
            report.append(f"{step}\n")

        return ''.join(report)


def main():
    """Run the script decomposer."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python script_decomposer.py <file_path>")
        sys.exit(1)

    decomposer = ScriptDecomposer()
    plan = decomposer.analyze_file(sys.argv[1])
    report = decomposer.generate_report(plan)
    print(report)


if __name__ == '__main__':
    main()
