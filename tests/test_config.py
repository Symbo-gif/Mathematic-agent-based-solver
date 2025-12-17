# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
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
Configuration System Tests
==========================

Tests for the centralized configuration system covering:
- Default value loading
- Environment variable overrides
- Configuration file loading (YAML/JSON)
- Validation
- Type coercion
"""

import os
import json
import tempfile
import pytest
from pathlib import Path


class TestConfigDefaults:
    """Test default configuration values."""

    def test_config_module_imports(self):
        """Configuration module should import successfully."""
        from symbo_agentic_reasoners.config import (
            Config, get_config, reload_config,
            HardwareConfig, ResourceThresholds, TimeoutConfig
        )
        assert Config is not None
        assert get_config is not None

    def test_get_config_returns_singleton(self):
        """get_config should return the same instance."""
        from symbo_agentic_reasoners.config import get_config, reload_config

        # Reset to ensure clean state
        reload_config()

        config1 = get_config()
        config2 = get_config()

        assert config1 is config2

    def test_hardware_defaults(self):
        """Hardware config should have sensible defaults."""
        from symbo_agentic_reasoners.config import get_config, reload_config

        reload_config()
        config = get_config()

        assert config.hardware.max_vram_gb == 8.0
        assert config.hardware.max_ram_gb == 32.0
        assert config.hardware.max_cpu_cores == 8
        assert config.hardware.llm_vram_requirement_gb == 5.5

    def test_threshold_defaults(self):
        """Threshold config should have sensible defaults."""
        from symbo_agentic_reasoners.config import get_config, reload_config

        reload_config()
        config = get_config()

        # VRAM thresholds
        assert config.thresholds.vram_warning == 0.85
        assert config.thresholds.vram_threshold == 0.90
        assert config.thresholds.vram_critical == 0.95
        assert config.thresholds.vram_emergency == 0.98

        # RAM thresholds
        assert config.thresholds.ram_warning == 0.80
        assert config.thresholds.ram_threshold == 0.85

    def test_timeout_defaults(self):
        """Timeout config should have sensible defaults."""
        from symbo_agentic_reasoners.config import get_config, reload_config

        reload_config()
        config = get_config()

        assert config.timeouts.default == 60.0
        assert config.timeouts.llm_inference == 120.0
        assert config.timeouts.integration == 180.0
        assert config.timeouts.proof == 300.0

    def test_agent_pool_defaults(self):
        """Agent pool config should have sensible defaults."""
        from symbo_agentic_reasoners.config import get_config, reload_config

        reload_config()
        config = get_config()

        assert config.agent_pool.max_active_agents == 8
        assert config.agent_pool.max_cognitive_agents == 1  # One-Model-At-A-Time
        assert config.agent_pool.specialist_standby_timeout == 300.0


class TestConfigValidation:
    """Test configuration validation."""

    def test_valid_config_passes_validation(self):
        """Default config should pass validation."""
        from symbo_agentic_reasoners.config import Config

        config = Config()
        errors = config.validate()

        assert errors == []

    def test_invalid_threshold_ordering_fails(self):
        """Thresholds out of order should fail validation."""
        from symbo_agentic_reasoners.config import Config, ResourceThresholds

        config = Config()
        # Set warning higher than threshold (invalid)
        config.thresholds.vram_warning = 0.95
        config.thresholds.vram_threshold = 0.90

        errors = config.validate()

        assert len(errors) > 0
        assert any("VRAM thresholds" in e for e in errors)

    def test_negative_timeout_fails(self):
        """Negative timeout should fail validation."""
        from symbo_agentic_reasoners.config import Config

        config = Config()
        config.timeouts.default = -1.0

        errors = config.validate()

        assert len(errors) > 0
        assert any("default" in e.lower() and "positive" in e.lower() for e in errors)


class TestEnvironmentOverrides:
    """Test environment variable configuration overrides."""

    def test_hardware_env_override(self):
        """Environment variables should override hardware config."""
        from symbo_agentic_reasoners.config import reload_config

        # Set env var
        os.environ["SYMBO_HARDWARE_MAX_VRAM_GB"] = "16.0"

        try:
            config = reload_config()
            assert config.hardware.max_vram_gb == 16.0
        finally:
            # Cleanup
            del os.environ["SYMBO_HARDWARE_MAX_VRAM_GB"]
            reload_config()

    def test_threshold_env_override(self):
        """Environment variables should override threshold config."""
        from symbo_agentic_reasoners.config import reload_config

        os.environ["SYMBO_THRESHOLDS_VRAM_WARNING"] = "0.75"

        try:
            config = reload_config()
            assert config.thresholds.vram_warning == 0.75
        finally:
            del os.environ["SYMBO_THRESHOLDS_VRAM_WARNING"]
            reload_config()

    def test_timeout_env_override(self):
        """Environment variables should override timeout config."""
        from symbo_agentic_reasoners.config import reload_config

        os.environ["SYMBO_TIMEOUTS_DEFAULT"] = "120.0"

        try:
            config = reload_config()
            assert config.timeouts.default == 120.0
        finally:
            del os.environ["SYMBO_TIMEOUTS_DEFAULT"]
            reload_config()


class TestFileConfiguration:
    """Test configuration file loading."""

    def test_load_json_config(self):
        """Should load configuration from JSON file."""
        from symbo_agentic_reasoners.config import Config

        config_data = {
            "hardware": {
                "max_vram_gb": 24.0,
                "max_ram_gb": 64.0
            },
            "thresholds": {
                "vram_warning": 0.80
            },
            "timeouts": {
                "default": 90.0
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_file = f.name

        try:
            config = Config()
            config.load_from_file(config_file)

            assert config.hardware.max_vram_gb == 24.0
            assert config.hardware.max_ram_gb == 64.0
            assert config.thresholds.vram_warning == 0.80
            assert config.timeouts.default == 90.0
        finally:
            os.unlink(config_file)

    def test_missing_config_file_warns(self):
        """Missing config file should log warning but not crash."""
        from symbo_agentic_reasoners.config import Config

        config = Config()
        # Should not raise
        config.load_from_file("/nonexistent/config.json")

        # Config should still have defaults
        assert config.hardware.max_vram_gb == 8.0

    def test_save_config_to_json(self):
        """Should save configuration to JSON file."""
        from symbo_agentic_reasoners.config import Config

        config = Config()
        config.hardware.max_vram_gb = 12.0

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_file = f.name

        try:
            config.save_to_file(config_file)

            with open(config_file) as f:
                saved_data = json.load(f)

            assert saved_data["hardware"]["max_vram_gb"] == 12.0
        finally:
            os.unlink(config_file)


class TestConfigDictConversion:
    """Test configuration dictionary conversion."""

    def test_to_dict(self):
        """Config should convert to dictionary."""
        from symbo_agentic_reasoners.config import Config

        config = Config()
        data = config.to_dict()

        assert "hardware" in data
        assert "thresholds" in data
        assert "timeouts" in data
        assert data["hardware"]["max_vram_gb"] == 8.0

    def test_config_is_serializable(self):
        """Config dictionary should be JSON serializable."""
        from symbo_agentic_reasoners.config import Config

        config = Config()
        data = config.to_dict()

        # Should not raise
        json_str = json.dumps(data)
        assert len(json_str) > 0


class TestTimeoutHelpers:
    """Test timeout configuration helpers."""

    def test_get_timeout_returns_value(self):
        """get_timeout should return configured value."""
        from symbo_agentic_reasoners.config import get_config, reload_config

        reload_config()
        config = get_config()

        assert config.timeouts.get_timeout("integration") == 180.0
        assert config.timeouts.get_timeout("proof") == 300.0

    def test_get_timeout_returns_default_for_unknown(self):
        """get_timeout should return default for unknown operation."""
        from symbo_agentic_reasoners.config import get_config, reload_config

        reload_config()
        config = get_config()

        # Unknown operation should fall back to default
        result = config.timeouts.get_timeout("unknown_operation")
        assert result == config.timeouts.default


class TestHardwareHelpers:
    """Test hardware configuration helpers."""

    def test_available_vram(self):
        """available_vram_gb should subtract infrastructure reserve."""
        from symbo_agentic_reasoners.config import HardwareConfig

        hw = HardwareConfig(max_vram_gb=8.0, infrastructural_vram_gb=0.5)

        assert hw.available_vram_gb() == 7.5

    def test_can_load_llm_true(self):
        """can_load_llm should return True when enough VRAM."""
        from symbo_agentic_reasoners.config import HardwareConfig

        hw = HardwareConfig(
            max_vram_gb=8.0,
            infrastructural_vram_gb=0.5,
            llm_vram_requirement_gb=5.5
        )

        assert hw.can_load_llm() is True  # 7.5 available > 5.5 required

    def test_can_load_llm_false(self):
        """can_load_llm should return False when not enough VRAM."""
        from symbo_agentic_reasoners.config import HardwareConfig

        hw = HardwareConfig(
            max_vram_gb=4.0,  # Small GPU
            infrastructural_vram_gb=0.5,
            llm_vram_requirement_gb=5.5
        )

        assert hw.can_load_llm() is False  # 3.5 available < 5.5 required


class TestPathConfiguration:
    """Test path configuration."""

    def test_default_paths(self):
        """Path config should have sensible defaults."""
        from symbo_agentic_reasoners.config import PathConfig

        paths = PathConfig()

        assert paths.data_dir == "data"
        assert paths.logs_dir == "data/logs"
        assert paths.traces_dir == "data/traces"

    def test_get_absolute_path(self):
        """get_absolute_path should resolve relative paths."""
        from symbo_agentic_reasoners.config import PathConfig

        paths = PathConfig()
        project_root = Path("/test/project")

        abs_path = paths.get_absolute_path("data/logs", project_root)

        assert abs_path == Path("/test/project/data/logs")


class TestAMSConfigIntegration:
    """Test AMS uses configuration system."""

    def test_ams_loads_from_config(self):
        """AMS should load values from configuration."""
        from symbo_agentic_reasoners.infrastructure import ams

        # Check that AMS module has the expected thresholds
        # These should match config defaults
        assert hasattr(ams, 'MAX_VRAM_GB')
        assert hasattr(ams, 'VRAM_THRESHOLD')
        assert hasattr(ams, 'VRAM_WARNING_THRESHOLD')

        # Values should be reasonable (defaults or from config)
        assert 0 < ams.MAX_VRAM_GB <= 128  # Reasonable VRAM range
        assert 0 < ams.VRAM_THRESHOLD <= 1.0
        assert 0 < ams.VRAM_WARNING_THRESHOLD <= 1.0


class TestResourceCoordinatorConfigIntegration:
    """Test ResourceCoordinator uses configuration system."""

    def test_resource_limits_from_config(self):
        """ResourceLimits should load from configuration."""
        from symbo_agentic_reasoners.core.resource_coordinator import ResourceLimits

        # Test from_config class method
        limits = ResourceLimits.from_config()

        assert limits.max_active_agents > 0
        assert limits.max_parallel_workers > 0
        assert 0 < limits.cpu_warning_threshold <= 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
