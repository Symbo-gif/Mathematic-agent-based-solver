import json
import logging.config
from pathlib import Path


def test_logging_config_json_loads():
    config_path = Path(__file__).resolve().parents[2] / "config" / "logging.json"
    with config_path.open() as f:
        data = json.load(f)

    # basic shape
    assert data["version"] == 1
    assert "formatters" in data and "handlers" in data
    assert set(data["handlers"]).issuperset({"console", "file"})


def test_logging_config_applies():
    """Ensure dictConfig consumes the file without raising."""
    config_path = Path(__file__).resolve().parents[2] / "config" / "logging.json"
    with config_path.open() as f:
        config = json.load(f)

    log_dir = Path(config["handlers"]["file"]["filename"]).parent
    log_dir.mkdir(parents=True, exist_ok=True)

    logging.config.dictConfig(config)
    logger = logging.getLogger("symbo.test")
    logger.info("structured log smoke test")
