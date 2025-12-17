# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
Comprehensive tests for cli.py to achieve 75%+ coverage.

Tests cover:
- MathSolverCLI initialization
- solve_problem method
- batch_process method
- Command handlers
- Status display
- Help display
- File loading utilities
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from io import StringIO


class TestMathSolverCLIInit:
    """Tests for MathSolverCLI initialization."""

    def test_init(self):
        """Test basic initialization."""
        from symbo_agentic_reasoners.cli import MathSolverCLI
        cli = MathSolverCLI()
        assert cli._system is None
        assert cli._solver is None
        assert cli._coordinator is None
        assert cli._initialized is False

    def test_banner_exists(self):
        """Test that BANNER constant exists."""
        from symbo_agentic_reasoners.cli import MathSolverCLI
        assert MathSolverCLI.BANNER is not None
        assert 'SYMBO' in MathSolverCLI.BANNER


class TestMathSolverCLISolve:
    """Tests for solve_problem method."""

    def test_solve_problem_fallback_success(self):
        """Test solve_problem with SymPy fallback on success."""
        from symbo_agentic_reasoners.cli import MathSolverCLI
        cli = MathSolverCLI()
        cli._initialized = True  # Skip initialization
        cli._solver = None  # Force fallback

        result = cli.solve_problem("2 + 2")
        assert result['status'] == 'success'
        assert result['result'] == '4'
        # native_symbolic is the fallback since we removed SymPy
        assert result['specialist'] == 'native_symbolic'

    def test_solve_problem_fallback_failure(self):
        """Test solve_problem with SymPy fallback on failure."""
        from symbo_agentic_reasoners.cli import MathSolverCLI
        cli = MathSolverCLI()
        cli._initialized = True
        cli._solver = None

        result = cli.solve_problem("invalid_syntax(((")
        assert result['status'] == 'failed'
        assert result['error'] is not None

    def test_solve_problem_with_solver(self):
        """Test solve_problem with actual solver."""
        from symbo_agentic_reasoners.cli import MathSolverCLI
        cli = MathSolverCLI()
        cli._initialized = True

        # Mock the solver
        mock_result = Mock()
        mock_result.status = Mock()
        mock_result.status.value = 'success'
        mock_result.result = '4'
        mock_result.problem_type = 'arithmetic'
        mock_result.domain = 'algebra'
        mock_result.specialist_used = 'arithmetic_specialist'
        mock_result.error = None

        mock_solver = Mock()
        mock_solver.solve = Mock(return_value=mock_result)
        cli._solver = mock_solver

        result = cli.solve_problem("2 + 2")
        assert result['status'] == 'success'
        assert result['result'] == '4'

    def test_solve_problem_solver_exception(self):
        """Test solve_problem when solver raises exception."""
        from symbo_agentic_reasoners.cli import MathSolverCLI
        cli = MathSolverCLI()
        cli._initialized = True

        mock_solver = Mock()
        mock_solver.solve = Mock(side_effect=Exception("Solver error"))
        cli._solver = mock_solver

        result = cli.solve_problem("2 + 2")
        assert result['status'] == 'failed'
        assert 'Solver error' in result['error']


class TestMathSolverCLICommands:
    """Tests for command handling."""

    def test_handle_command_help(self, capsys):
        """Test :help command."""
        from symbo_agentic_reasoners.cli import MathSolverCLI
        cli = MathSolverCLI()
        cli._handle_command(':help')
        captured = capsys.readouterr()
        assert 'Available Commands' in captured.out

    def test_handle_command_h(self, capsys):
        """Test :h command."""
        from symbo_agentic_reasoners.cli import MathSolverCLI
        cli = MathSolverCLI()
        cli._handle_command(':h')
        captured = capsys.readouterr()
        assert 'Available Commands' in captured.out

    def test_handle_command_status_not_initialized(self, capsys):
        """Test :status command when not initialized."""
        from symbo_agentic_reasoners.cli import MathSolverCLI
        cli = MathSolverCLI()
        cli._handle_command(':status')
        captured = capsys.readouterr()
        assert 'SYSTEM STATUS' in captured.out
        assert 'Not initialized' in captured.out

    def test_handle_command_status_initialized(self, capsys):
        """Test :status command when initialized."""
        from symbo_agentic_reasoners.cli import MathSolverCLI
        cli = MathSolverCLI()
        cli._initialized = True
        cli._system = Mock()
        cli._system.health_check = Mock(return_value={'overall': True})
        cli._phase2 = Mock()
        cli._phase2.get_statistics = Mock(return_value={'agents_registered': 10})

        cli._handle_command(':status')
        captured = capsys.readouterr()
        assert 'SYSTEM STATUS' in captured.out

    def test_handle_command_batch_no_args(self, capsys):
        """Test :batch command without arguments."""
        from symbo_agentic_reasoners.cli import MathSolverCLI
        cli = MathSolverCLI()
        cli._handle_command(':batch')
        captured = capsys.readouterr()
        assert 'Usage' in captured.out

    def test_handle_command_agents_not_initialized(self, capsys):
        """Test :agents command when not initialized."""
        from symbo_agentic_reasoners.cli import MathSolverCLI
        cli = MathSolverCLI()
        cli._handle_command(':agents')
        captured = capsys.readouterr()
        assert 'not initialized' in captured.out.lower()

    def test_handle_command_agents_initialized(self, capsys):
        """Test :agents command when initialized."""
        from symbo_agentic_reasoners.cli import MathSolverCLI
        cli = MathSolverCLI()
        cli._initialized = True
        cli._system = Mock()
        cli._system.df = Mock()
        cli._system.df.list_all_services = Mock(return_value=['agent1', 'agent2'])
        cli._phase2 = Mock()

        cli._handle_command(':agents')
        captured = capsys.readouterr()
        assert 'REGISTERED AGENTS' in captured.out

    def test_handle_command_unknown(self, capsys):
        """Test unknown command."""
        from symbo_agentic_reasoners.cli import MathSolverCLI
        cli = MathSolverCLI()
        cli._handle_command(':unknown_cmd')
        captured = capsys.readouterr()
        assert 'Unknown command' in captured.out

    def test_handle_command_clear(self):
        """Test :clear command."""
        from symbo_agentic_reasoners.cli import MathSolverCLI
        cli = MathSolverCLI()
        with patch('os.system') as mock_system:
            cli._handle_command(':clear')
            mock_system.assert_called_once()


class TestMathSolverCLIBatch:
    """Tests for batch processing."""

    def test_batch_process_nonexistent_path(self, capsys):
        """Test batch_process with non-existent path."""
        from symbo_agentic_reasoners.cli import MathSolverCLI
        cli = MathSolverCLI()
        cli._initialized = True
        cli._solver = None

        cli.batch_process('/nonexistent/path/xyz123')
        captured = capsys.readouterr()
        assert 'does not exist' in captured.out

    def test_batch_process_txt_file(self, capsys, tmp_path):
        """Test batch_process with txt file."""
        from symbo_agentic_reasoners.cli import MathSolverCLI
        cli = MathSolverCLI()
        cli._initialized = True
        cli._solver = None

        # Create test file
        test_file = tmp_path / "problems.txt"
        test_file.write_text("2 + 2\n3 * 3\n# comment line\n")

        cli.batch_process(str(test_file))
        captured = capsys.readouterr()
        assert 'BATCH COMPLETE' in captured.out
        assert '2/2' in captured.out  # Both should succeed

    def test_batch_process_json_file(self, capsys, tmp_path):
        """Test batch_process with JSON file."""
        from symbo_agentic_reasoners.cli import MathSolverCLI
        cli = MathSolverCLI()
        cli._initialized = True
        cli._solver = None

        # Create test file
        test_file = tmp_path / "problems.json"
        test_file.write_text(json.dumps(["1+1", "2+2", {"problem": "3+3"}]))

        cli.batch_process(str(test_file))
        captured = capsys.readouterr()
        assert 'BATCH COMPLETE' in captured.out

    def test_batch_process_json_with_problems_key(self, capsys, tmp_path):
        """Test batch_process with JSON file having 'problems' key."""
        from symbo_agentic_reasoners.cli import MathSolverCLI
        cli = MathSolverCLI()
        cli._initialized = True
        cli._solver = None

        # Create test file
        test_file = tmp_path / "problems.json"
        test_file.write_text(json.dumps({
            "problems": [{"problem": "1+1"}, {"problem": "2+2"}]
        }))

        cli.batch_process(str(test_file))
        captured = capsys.readouterr()
        assert 'BATCH COMPLETE' in captured.out

    def test_batch_process_folder(self, capsys, tmp_path):
        """Test batch_process with folder."""
        from symbo_agentic_reasoners.cli import MathSolverCLI
        cli = MathSolverCLI()
        cli._initialized = True
        cli._solver = None

        # Create test files
        (tmp_path / "file1.txt").write_text("1+1\n")
        (tmp_path / "file2.txt").write_text("2+2\n")
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "file3.txt").write_text("3+3\n")

        cli.batch_process(str(tmp_path))
        captured = capsys.readouterr()
        assert 'BATCH COMPLETE' in captured.out

    def test_batch_process_empty_folder(self, capsys, tmp_path):
        """Test batch_process with empty folder."""
        from symbo_agentic_reasoners.cli import MathSolverCLI
        cli = MathSolverCLI()
        cli._initialized = True
        cli._solver = None

        # Create empty subfolder
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        cli.batch_process(str(empty_dir))
        captured = capsys.readouterr()
        assert 'No problems found' in captured.out

    def test_batch_process_with_output_path(self, capsys, tmp_path):
        """Test batch_process with custom output path."""
        from symbo_agentic_reasoners.cli import MathSolverCLI
        cli = MathSolverCLI()
        cli._initialized = True
        cli._solver = None

        # Create test file
        test_file = tmp_path / "problems.txt"
        test_file.write_text("1+1\n")
        output_file = tmp_path / "results.json"

        cli.batch_process(str(test_file), output_path=str(output_file))

        assert output_file.exists()
        with open(output_file) as f:
            data = json.load(f)
        assert 'results' in data


class TestMathSolverCLIFileLoading:
    """Tests for file loading utilities."""

    def test_load_problems_from_txt(self, tmp_path):
        """Test loading problems from txt file."""
        from symbo_agentic_reasoners.cli import MathSolverCLI
        cli = MathSolverCLI()

        test_file = tmp_path / "test.txt"
        test_file.write_text("problem1\nproblem2\n# comment\n\nproblem3")

        problems = cli._load_problems_from_file(test_file)
        assert len(problems) == 3

    def test_load_problems_from_json_list(self, tmp_path):
        """Test loading problems from JSON list."""
        from symbo_agentic_reasoners.cli import MathSolverCLI
        cli = MathSolverCLI()

        test_file = tmp_path / "test.json"
        test_file.write_text(json.dumps(["p1", "p2", {"problem": "p3"}]))

        problems = cli._load_problems_from_file(test_file)
        assert len(problems) == 3

    def test_load_problems_from_md(self, tmp_path):
        """Test loading problems from markdown file."""
        from symbo_agentic_reasoners.cli import MathSolverCLI
        cli = MathSolverCLI()

        test_file = tmp_path / "test.md"
        test_file.write_text("# Header\nproblem1\nproblem2")

        problems = cli._load_problems_from_file(test_file)
        # Header line starting with # is skipped
        assert len(problems) == 2

    def test_load_problems_invalid_file(self, tmp_path, capsys):
        """Test loading problems from invalid file."""
        from symbo_agentic_reasoners.cli import MathSolverCLI
        cli = MathSolverCLI()

        test_file = tmp_path / "test.json"
        test_file.write_text("invalid json {{{")

        problems = cli._load_problems_from_file(test_file)
        captured = capsys.readouterr()
        assert problems == []
        assert 'Failed to load' in captured.out


class TestMathSolverCLIDisplay:
    """Tests for display methods."""

    def test_display_result_success(self, capsys):
        """Test displaying successful result."""
        from symbo_agentic_reasoners.cli import MathSolverCLI
        cli = MathSolverCLI()

        result = {
            'status': 'success',
            'result': '4',
            'domain': 'algebra',
            'specialist': 'arithmetic',
            'time_ms': 10.5
        }

        cli._display_result("2+2", result)
        captured = capsys.readouterr()
        assert '4' in captured.out
        assert 'algebra' in captured.out

    def test_display_result_failure(self, capsys):
        """Test displaying failed result."""
        from symbo_agentic_reasoners.cli import MathSolverCLI
        cli = MathSolverCLI()

        result = {
            'status': 'failed',
            'error': 'Parse error',
            'time_ms': 5.0
        }

        cli._display_result("invalid", result)
        captured = capsys.readouterr()
        assert 'Failed' in captured.out
        assert 'Parse error' in captured.out

    def test_show_help(self, capsys):
        """Test showing help."""
        from symbo_agentic_reasoners.cli import MathSolverCLI
        cli = MathSolverCLI()
        cli._show_help()
        captured = capsys.readouterr()
        assert 'Available Commands' in captured.out
        assert ':quit' in captured.out
        assert ':help' in captured.out


class TestMathSolverCLIShutdown:
    """Tests for shutdown methods."""

    def test_shutdown_graceful(self):
        """Test graceful shutdown."""
        from symbo_agentic_reasoners.cli import MathSolverCLI
        cli = MathSolverCLI()

        mock_coordinator = Mock()
        mock_system = Mock()
        cli._coordinator = mock_coordinator
        cli._system = mock_system

        cli._shutdown()

        mock_coordinator.stop.assert_called_once_with(save_state=True)
        mock_system.shutdown.assert_called_once()

    def test_shutdown_with_exception(self):
        """Test shutdown handles exceptions."""
        from symbo_agentic_reasoners.cli import MathSolverCLI
        cli = MathSolverCLI()

        mock_coordinator = Mock()
        mock_coordinator.stop = Mock(side_effect=Exception("Stop error"))
        cli._coordinator = mock_coordinator

        # Should not raise
        cli._shutdown()

    def test_emergency_shutdown(self, capsys):
        """Test emergency shutdown."""
        from symbo_agentic_reasoners.cli import MathSolverCLI
        cli = MathSolverCLI()

        mock_coordinator = Mock()
        mock_system = Mock()
        cli._coordinator = mock_coordinator
        cli._system = mock_system

        cli._emergency_shutdown()

        captured = capsys.readouterr()
        assert 'EMERGENCY SHUTDOWN' in captured.out
        mock_coordinator.stop.assert_called_once_with(save_state=False)

    def test_emergency_shutdown_with_error(self, capsys):
        """Test emergency shutdown with error."""
        from symbo_agentic_reasoners.cli import MathSolverCLI
        cli = MathSolverCLI()

        mock_coordinator = Mock()
        mock_coordinator.stop = Mock(side_effect=Exception("Emergency error"))
        cli._coordinator = mock_coordinator

        cli._emergency_shutdown()

        captured = capsys.readouterr()
        assert 'EMERGENCY SHUTDOWN' in captured.out
        assert 'error' in captured.out.lower()


class TestMathSolverCLIStatus:
    """Tests for status display."""

    def test_show_status_without_psutil(self, capsys):
        """Test status without psutil."""
        from symbo_agentic_reasoners.cli import MathSolverCLI
        cli = MathSolverCLI()

        with patch.dict('sys.modules', {'psutil': None}):
            with patch('builtins.__import__', side_effect=ImportError):
                cli._show_status()

        captured = capsys.readouterr()
        assert 'SYSTEM STATUS' in captured.out

    def test_show_status_with_psutil(self, capsys):
        """Test status with psutil mocked."""
        from symbo_agentic_reasoners.cli import MathSolverCLI
        cli = MathSolverCLI()

        mock_psutil = Mock()
        mock_psutil.cpu_percent = Mock(return_value=25.0)
        mock_memory = Mock()
        mock_memory.percent = 50.0
        mock_memory.used = 8 * (1024**3)
        mock_memory.total = 16 * (1024**3)
        mock_psutil.virtual_memory = Mock(return_value=mock_memory)

        with patch.dict('sys.modules', {'psutil': mock_psutil}):
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(returncode=1)  # nvidia-smi fails
                cli._show_status()

        captured = capsys.readouterr()
        assert 'SYSTEM STATUS' in captured.out

    def test_show_status_with_gpu(self, capsys):
        """Test status with GPU info."""
        from symbo_agentic_reasoners.cli import MathSolverCLI
        cli = MathSolverCLI()

        mock_psutil = Mock()
        mock_psutil.cpu_percent = Mock(return_value=25.0)
        mock_memory = Mock()
        mock_memory.percent = 50.0
        mock_memory.used = 8 * (1024**3)
        mock_memory.total = 16 * (1024**3)
        mock_psutil.virtual_memory = Mock(return_value=mock_memory)

        with patch.dict('sys.modules', {'psutil': mock_psutil}):
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(returncode=0, stdout="50, 4000, 8000")
                cli._show_status()

        captured = capsys.readouterr()
        assert 'SYSTEM STATUS' in captured.out

    def test_show_status_system_health_error(self, capsys):
        """Test status when system health check fails."""
        from symbo_agentic_reasoners.cli import MathSolverCLI
        cli = MathSolverCLI()
        cli._initialized = True
        cli._system = Mock()
        cli._system.health_check = Mock(side_effect=Exception("Health check error"))

        with patch.dict('sys.modules', {'psutil': None}):
            with patch('builtins.__import__', side_effect=ImportError):
                cli._show_status()

        captured = capsys.readouterr()
        assert 'unavailable' in captured.out.lower()


class TestMainFunction:
    """Tests for main entry point."""

    def test_main_solve_success(self, capsys):
        """Test main with solve command success."""
        from symbo_agentic_reasoners.cli import main, MathSolverCLI

        with patch('sys.argv', ['cli', 'solve', '2+2']):
            with patch.object(MathSolverCLI, '_initialize_system'):
                with patch.object(MathSolverCLI, 'solve_problem') as mock_solve:
                    mock_solve.return_value = {
                        'status': 'success',
                        'result': '4',
                        'domain': 'algebra',
                        'specialist': 'arith'
                    }
                    main()

        captured = capsys.readouterr()
        assert '4' in captured.out

    def test_main_solve_failure(self, capsys):
        """Test main with solve command failure."""
        from symbo_agentic_reasoners.cli import main, MathSolverCLI

        with patch('sys.argv', ['cli', 'solve', 'invalid']):
            with patch.object(MathSolverCLI, '_initialize_system'):
                with patch.object(MathSolverCLI, 'solve_problem') as mock_solve:
                    mock_solve.return_value = {
                        'status': 'failed',
                        'error': 'Parse error'
                    }
                    with pytest.raises(SystemExit) as exc_info:
                        main()
                    assert exc_info.value.code == 1

    def test_main_solve_verbose(self, capsys):
        """Test main with solve command in verbose mode."""
        from symbo_agentic_reasoners.cli import main, MathSolverCLI

        with patch('sys.argv', ['cli', 'solve', '2+2', '-v']):
            with patch.object(MathSolverCLI, '_initialize_system'):
                with patch.object(MathSolverCLI, 'solve_problem') as mock_solve:
                    mock_solve.return_value = {
                        'status': 'success',
                        'result': '4',
                        'domain': 'algebra',
                        'specialist': 'arith',
                        'time_ms': 10.0
                    }
                    main()

        captured = capsys.readouterr()
        assert '4' in captured.out
        assert 'algebra' in captured.out

    def test_main_batch(self, tmp_path, capsys):
        """Test main with batch command."""
        from symbo_agentic_reasoners.cli import main, MathSolverCLI

        test_file = tmp_path / "test.txt"
        test_file.write_text("1+1\n")

        with patch('sys.argv', ['cli', 'batch', str(test_file)]):
            with patch.object(MathSolverCLI, '_initialize_system'):
                with patch.object(MathSolverCLI, 'solve_problem') as mock_solve:
                    mock_solve.return_value = {'status': 'success', 'result': '2'}
                    main()

        captured = capsys.readouterr()
        assert 'BATCH' in captured.out

    def test_main_status(self, capsys):
        """Test main with status command."""
        from symbo_agentic_reasoners.cli import main, MathSolverCLI

        with patch('sys.argv', ['cli', 'status']):
            with patch.object(MathSolverCLI, '_initialize_system'):
                with patch.object(MathSolverCLI, '_show_status'):
                    main()


class TestCLIInitializeSystem:
    """Tests for system initialization."""

    def test_initialize_already_initialized(self):
        """Test that initialization is skipped if already done."""
        from symbo_agentic_reasoners.cli import MathSolverCLI
        cli = MathSolverCLI()
        cli._initialized = True

        # Should return immediately without doing anything
        cli._initialize_system(verbose=True)
        assert cli._initialized is True

    def test_initialize_system_failure(self, capsys):
        """Test initialization failure handling."""
        from symbo_agentic_reasoners.cli import MathSolverCLI
        cli = MathSolverCLI()

        with patch('symbo_agentic_reasoners.core.system.Phase0System', side_effect=Exception("Init error")):
            cli._initialize_system(verbose=True)

        captured = capsys.readouterr()
        assert 'ERROR' in captured.out
        assert cli._initialized is True  # Still marked as initialized
