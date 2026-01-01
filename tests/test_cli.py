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
Tests for CLI and Batch Processor
==================================

Tests the user-facing interfaces:
- CLI solve functionality
- Batch processing from files/folders
- Result export
"""

import pytest
import json
import tempfile
import os
from pathlib import Path

from symbo_agentic_reasoners.cli import MathSolverCLI
from symbo_agentic_reasoners.batch_processor import (
    BatchProcessor, BatchResult, ProblemItem, ProcessingStatus,
    process_problems, process_file
)


class TestCLISolve:
    """Tests for CLI solve functionality."""

    def test_solve_simple_arithmetic(self):
        """Test solving simple arithmetic."""
        cli = MathSolverCLI()
        result = cli.solve_problem("2 + 2")
        assert result['status'] == 'success'
        assert '4' in str(result['result'])

    def test_solve_algebra(self):
        """Test solving algebraic expression."""
        cli = MathSolverCLI()
        result = cli.solve_problem("x**2 - 4")
        assert result['status'] == 'success'

    def test_solve_differentiation(self):
        """Test differentiation."""
        cli = MathSolverCLI()
        result = cli.solve_problem("diff(x**2, x)")
        assert result['status'] == 'success'
        # Result should be 2*x
        assert '2' in str(result['result'])

    def test_solve_integration(self):
        """Test integration."""
        cli = MathSolverCLI()
        result = cli.solve_problem("integrate(x, x)")
        assert result['status'] == 'success'
        # Result should contain x**2
        assert 'x**2' in str(result['result']) or '2' in str(result['result'])

    def test_solve_returns_time(self):
        """Test that solve returns timing info."""
        cli = MathSolverCLI()
        result = cli.solve_problem("1 + 1")
        assert 'time_ms' in result
        assert result['time_ms'] >= 0

    def test_solve_invalid_expression(self):
        """Test handling of invalid expressions."""
        cli = MathSolverCLI()
        result = cli.solve_problem("not a valid expression @#$%")
        # Should fail gracefully
        assert result is not None


class TestBatchProcessor:
    """Tests for batch processing functionality."""

    def test_process_list_of_problems(self):
        """Test processing a list of problems."""
        processor = BatchProcessor(max_workers=1)
        problems = ["2+2", "3*3", "10/2"]

        result = processor.process_problems(problems)

        assert isinstance(result, BatchResult)
        assert result.total_problems == 3
        assert result.solved >= 1  # At least some should solve

    def test_batch_result_has_required_fields(self):
        """Test that BatchResult has all required fields."""
        processor = BatchProcessor(max_workers=1)
        result = processor.process_problems(["1+1"])

        assert hasattr(result, 'batch_id')
        assert hasattr(result, 'start_time')
        assert hasattr(result, 'total_problems')
        assert hasattr(result, 'solved')
        assert hasattr(result, 'failed')
        assert hasattr(result, 'items')

    def test_process_file_txt(self):
        """Test processing a .txt file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test file
            test_file = Path(tmpdir) / "problems.txt"
            test_file.write_text("2+2\n3+3\n4+4\n")

            processor = BatchProcessor(max_workers=1)
            result = processor.process_file(str(test_file))

            assert result.total_problems == 3

    def test_process_file_json(self):
        """Test processing a .json file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test file
            test_file = Path(tmpdir) / "problems.json"
            test_file.write_text(json.dumps([
                "5+5",
                {"problem": "6+6"},
                "7+7"
            ]))

            processor = BatchProcessor(max_workers=1)
            result = processor.process_file(str(test_file))

            assert result.total_problems == 3

    def test_process_folder(self):
        """Test processing a folder of files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            (Path(tmpdir) / "file1.txt").write_text("1+1\n2+2\n")
            (Path(tmpdir) / "file2.txt").write_text("3+3\n4+4\n")

            processor = BatchProcessor(max_workers=1)
            result = processor.process_folder(tmpdir)

            assert result.total_problems == 4

    def test_export_json(self):
        """Test exporting results to JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            processor = BatchProcessor(max_workers=1)
            result = processor.process_problems(["1+1", "2+2"])

            output_path = Path(tmpdir) / "results.json"
            processor.export_results(result, str(output_path), format='json')

            assert output_path.exists()

            # Verify JSON structure
            with open(output_path) as f:
                data = json.load(f)
            assert 'batch_id' in data
            assert 'items' in data

    def test_export_csv(self):
        """Test exporting results to CSV."""
        with tempfile.TemporaryDirectory() as tmpdir:
            processor = BatchProcessor(max_workers=1)
            result = processor.process_problems(["1+1"])

            output_path = Path(tmpdir) / "results.csv"
            processor.export_results(result, str(output_path), format='csv')

            assert output_path.exists()
            content = output_path.read_text()
            assert 'id,problem,status' in content

    def test_progress_callback(self):
        """Test progress callback is called."""
        progress_calls = []

        def callback(current, total, item):
            progress_calls.append((current, total))

        processor = BatchProcessor(max_workers=1, progress_callback=callback)
        processor.process_problems(["1+1", "2+2", "3+3"])

        assert len(progress_calls) == 3
        assert progress_calls[-1][0] == 3  # Final call should be 3/3


class TestProblemItem:
    """Tests for ProblemItem data class."""

    def test_problem_item_creation(self):
        """Test creating a ProblemItem."""
        item = ProblemItem(
            id="test_001",
            problem="2+2",
            source_file="test.txt"
        )
        assert item.id == "test_001"
        assert item.problem == "2+2"
        assert item.status == ProcessingStatus.PENDING

    def test_problem_item_metadata(self):
        """Test ProblemItem metadata."""
        item = ProblemItem(
            id="test_002",
            problem="x+y",
            metadata={'category': 'algebra', 'difficulty': 'easy'}
        )
        assert item.metadata['category'] == 'algebra'


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_process_problems_function(self):
        """Test process_problems convenience function."""
        result = process_problems(["1+1", "2+2"])
        assert result.total_problems == 2

    def test_process_file_function(self):
        """Test process_file convenience function."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("5+5")

            result = process_file(str(test_file))
            assert result.total_problems == 1


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_problem_list(self):
        """Test processing empty problem list."""
        processor = BatchProcessor()
        result = processor.process_problems([])
        assert result.total_problems == 0
        assert result.solved == 0

    def test_nonexistent_file(self):
        """Test handling of nonexistent file."""
        processor = BatchProcessor()
        with pytest.raises(ValueError):
            processor.process_file("/nonexistent/path/file.txt")

    def test_nonexistent_folder(self):
        """Test handling of nonexistent folder."""
        processor = BatchProcessor()
        with pytest.raises(ValueError):
            processor.process_folder("/nonexistent/path/")

    def test_skip_comments_in_txt(self):
        """Test that comments are skipped in text files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "with_comments.txt"
            test_file.write_text("# This is a comment\n1+1\n// Another comment\n2+2\n")

            processor = BatchProcessor(max_workers=1)
            result = processor.process_file(str(test_file))

            assert result.total_problems == 2  # Only non-comment lines
