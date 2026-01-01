import json
import logging.config
from pathlib import Path


def _find_logging_config() -> Path:
    """Locate the logging config starting from the test file upward."""
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "config" / "logging.json"
        if candidate.exists():
            return candidate
    raise FileNotFoundError("config/logging.json not found")


def test_logging_config_json_loads():
    config_path = _find_logging_config()
    with config_path.open() as f:
        data = json.load(f)

    # basic shape
    assert data["version"] == 1
    assert "formatters" in data and "handlers" in data
    assert set(data["handlers"]).issuperset({"console", "file"})


def test_logging_config_applies(tmp_path):
    """Ensure dictConfig consumes the file without raising."""
    config_path = _find_logging_config()
    with config_path.open() as f:
        config = json.load(f)

    config["handlers"]["file"]["filename"] = str(tmp_path / "symbo_agentic_reasoners.log")

    logging.config.dictConfig(config)
    logger = logging.getLogger("symbo.test")
    logger.info("structured log smoke test")
