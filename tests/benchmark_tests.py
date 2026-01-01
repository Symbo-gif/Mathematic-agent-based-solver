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

import pytest

# Optional dependency - skip tests if not available
try:
    from datasets import load_dataset
    HAS_DATASETS = True
except ImportError:
    HAS_DATASETS = False
    load_dataset = None

from symbo_agentic_reasoners.core.orchestrator import MainOrchestrator as OrchestratorAgent


def load_gsm8k_dataset():
    # Load GSM8K dataset for benchmarking
    return load_dataset('gsm8k', 'main')['test']


def load_math_dataset():
    # Load MATH dataset for benchmarking
    return load_dataset('competition_math')['test']


@pytest.mark.skipif(not HAS_DATASETS, reason="datasets library not installed")
def test_gsm8k_benchmark():
    orchestrator = OrchestratorAgent()
    dataset = load_gsm8k_dataset()
    results = []
    
    for i, example in enumerate(dataset):
        if i >= 100:  # Test first 100 examples
            break
            
        problem = example['question']
        expected_answer = example['answer']
        
        result = orchestrator.solve_problem(problem)
        
        # Compare with expected answer
        is_correct = _compare_answers(result['solution'], expected_answer)
        results.append(is_correct)
        
    accuracy = sum(results) / len(results)
    assert accuracy >= 0.95, f"GSM8K accuracy {accuracy:.2f} below threshold"
    
    # Write benchmark report
    with open('gsm8k_benchmark_report.txt', 'w') as f:
        f.write(f"GSM8K Benchmark Results\n")
        f.write(f"Total problems: {len(results)}\n")
        f.write(f"Correct answers: {sum(results)}\n")
        f.write(f"Accuracy: {accuracy:.4f}\n")
        

@pytest.mark.skipif(not HAS_DATASETS, reason="datasets library not installed")
def test_math_benchmark():
    orchestrator = OrchestratorAgent()
    dataset = load_math_dataset()
    results = []
    
    for i, example in enumerate(dataset):
        if i >= 100:  # Test first 100 examples
            break
            
        problem = f"{example['problem']} {example['type']}"
        expected_answer = example['solution']
        
        result = orchestrator.solve_problem(problem)
        
        # Compare with expected answer
        is_correct = _compare_answers(result['solution'], expected_answer)
        results.append(is_correct)
        
    accuracy = sum(results) / len(results)
    assert accuracy >= 0.92, f"MATH accuracy {accuracy:.2f} below threshold"
    
    # Write benchmark report
    with open('math_benchmark_report.txt', 'w') as f:
        f.write(f"MATH Benchmark Results\n")
        f.write(f"Total problems: {len(results)}\n")
        f.write(f"Correct answers: {sum(results)}\n")
        f.write(f"Accuracy: {accuracy:.4f}\n")
        

def _compare_answers(system_answer, expected_answer):
    # Implementation to compare answers with tolerance for mathematical equivalence
    # This would handle different forms of the same mathematical expression
    pass
