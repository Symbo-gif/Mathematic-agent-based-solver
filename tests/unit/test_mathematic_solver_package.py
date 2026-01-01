import importlib


def test_mathematic_solver_core_aliases():
    core = importlib.import_module("mathematic_solver.core")
    assert hasattr(core, "Blackboard")
    assert hasattr(core, "SolveStatus")


def test_mathematic_solver_cli_shim():
    cli = importlib.import_module("mathematic_solver.cli")
    assert hasattr(cli, "main")
