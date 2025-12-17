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
Centralized Configuration Settings
===================================

Type-safe configuration dataclasses with validation, environment variable
support, and file-based configuration loading.

Configuration Priority (highest to lowest):
1. Runtime overrides (config.set())
2. Environment variables (SYMBO_*)
3. Configuration file (config.yaml)
4. Default values (defined here)
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from pathlib import Path
import os
import json
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# HARDWARE CONFIGURATION
# ============================================================================

@dataclass
class HardwareConfig:
    """
    Hardware constraints for the system.

    These values should match your actual hardware capabilities.
    Default values are configured for RTX 4060 (8GB) + 32GB RAM + 8-core CPU.
    """
    # GPU Configuration
    max_vram_gb: float = 8.0
    llm_vram_requirement_gb: float = 5.5  # 7B model at 4-bit quantization
    infrastructural_vram_gb: float = 0.5  # Reserved for OS/drivers

    # System Memory
    max_ram_gb: float = 32.0

    # CPU Configuration
    max_cpu_cores: int = 8

    # GPU Detection
    gpu_name: str = "auto"  # "auto" to detect, or specify e.g. "RTX 4060"

    def available_vram_gb(self) -> float:
        """Calculate available VRAM after infrastructure reservation."""
        return self.max_vram_gb - self.infrastructural_vram_gb

    def can_load_llm(self) -> bool:
        """Check if system can load LLM model."""
        return self.available_vram_gb() >= self.llm_vram_requirement_gb


# ============================================================================
# RESOURCE THRESHOLDS
# ============================================================================

@dataclass
class ResourceThresholds:
    """
    Resource utilization thresholds for monitoring and emergency response.

    Values are expressed as fractions (0.0 to 1.0).
    """
    # VRAM Thresholds
    vram_warning: float = 0.85      # 85% - Start warning
    vram_threshold: float = 0.90    # 90% - Reject new cognitive agents
    vram_critical: float = 0.95     # 95% - Emergency state
    vram_emergency: float = 0.98    # 98% - Force shutdown

    # RAM Thresholds
    ram_warning: float = 0.80       # 80% - Start warning
    ram_threshold: float = 0.85     # 85% - Start throttling
    ram_critical: float = 0.92      # 92% - Emergency state
    ram_emergency: float = 0.95     # 95% - Force shutdown

    # CPU Thresholds
    cpu_warning: float = 0.80       # 80% - Start warning
    cpu_threshold: float = 0.90     # 90% - Sustained throttling
    cpu_critical: float = 0.95      # 95% - Emergency state

    # Disk Thresholds
    disk_warning: float = 0.90      # 90% - Start warning
    disk_critical: float = 0.95     # 95% - Emergency state

    def validate(self) -> List[str]:
        """Validate threshold ordering. Returns list of errors."""
        errors = []

        # VRAM ordering
        if not (self.vram_warning < self.vram_threshold < self.vram_critical < self.vram_emergency):
            errors.append("VRAM thresholds must be: warning < threshold < critical < emergency")

        # RAM ordering
        if not (self.ram_warning < self.ram_threshold < self.ram_critical < self.ram_emergency):
            errors.append("RAM thresholds must be: warning < threshold < critical < emergency")

        # CPU ordering
        if not (self.cpu_warning < self.cpu_threshold < self.cpu_critical):
            errors.append("CPU thresholds must be: warning < threshold < critical")

        # Range validation
        for name, value in [
            ("vram_emergency", self.vram_emergency),
            ("ram_emergency", self.ram_emergency),
            ("cpu_critical", self.cpu_critical),
            ("disk_critical", self.disk_critical),
        ]:
            if not (0.0 < value <= 1.0):
                errors.append(f"{name} must be between 0.0 and 1.0, got {value}")

        return errors


# ============================================================================
# TIMEOUT CONFIGURATION
# ============================================================================

@dataclass
class TimeoutConfig:
    """
    Timeout values for various operations (in seconds).
    """
    # General Operations
    default: float = 60.0

    # LLM Operations
    llm_inference: float = 120.0
    llm_generation: float = 180.0

    # Mathematical Operations
    symbolic_solve: float = 90.0
    integration: float = 180.0
    differentiation: float = 60.0
    proof: float = 300.0
    series_expansion: float = 120.0
    matrix_operations: float = 90.0

    # System Operations
    search: float = 30.0
    message: float = 10.0
    agent_activation: float = 30.0
    agent_deactivation: float = 10.0

    # External Queries
    nvidia_smi_query: float = 5.0
    gpu_memory_query: float = 5.0

    # Orchestration
    result_poll_interval: float = 0.5
    result_await_timeout: float = 30.0

    def get_timeout(self, operation_type: str) -> float:
        """Get timeout for operation type, with fallback to default."""
        return getattr(self, operation_type, self.default)


# ============================================================================
# AGENT POOL CONFIGURATION
# ============================================================================

@dataclass
class AgentPoolConfig:
    """
    Agent pool and lifecycle configuration.
    """
    # Concurrency Limits
    max_active_agents: int = 8
    max_parallel_workers: int = 4
    max_cognitive_agents: int = 1  # One-Model-At-A-Time rule

    # Standby Configuration (seconds)
    specialist_standby_timeout: float = 300.0   # 5 minutes
    supervisor_standby_timeout: float = 600.0   # 10 minutes
    orchestrator_standby_timeout: float = 900.0 # 15 minutes

    # Queue Configuration
    max_queue_size: int = 100
    queue_timeout: float = 30.0

    # Memory Limits
    max_memory_per_agent_mb: float = 512.0
    total_agent_memory_mb: float = 4096.0


# ============================================================================
# MONITORING CONFIGURATION
# ============================================================================

@dataclass
class MonitoringConfig:
    """
    Monitoring and health check configuration.
    """
    # Check Intervals (seconds)
    watchdog_check_interval: float = 1.0
    ams_monitor_interval: float = 5.0
    resource_monitor_interval: float = 5.0
    cpu_measurement_interval: float = 0.1

    # History & Tracking
    resource_history_size: int = 12      # ~1 minute at 5s intervals
    sustained_threshold_count: int = 3   # Consecutive checks before action

    # Thread Management
    thread_join_timeout: float = 2.0
    monitor_stop_timeout: float = 5.0

    # Batch Processing
    batch_poll_interval: float = 5.0
    batch_max_workers: int = 4
    batch_timeout_per_problem: float = 60.0


# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

@dataclass
class LoggingConfig:
    """
    Logging and tracing configuration.
    """
    # Log Levels
    default_level: str = "INFO"
    infrastructure_level: str = "INFO"
    agent_level: str = "INFO"
    protocol_level: str = "WARNING"

    # File Configuration
    log_to_file: bool = True
    log_file_max_bytes: int = 10 * 1024 * 1024  # 10 MB
    log_file_backup_count: int = 5

    # Format
    use_json_format: bool = False
    include_correlation_id: bool = True

    # Trace Logging
    trace_enabled: bool = True
    trace_max_files: int = 100


# ============================================================================
# PATH CONFIGURATION
# ============================================================================

@dataclass
class PathConfig:
    """
    File and directory path configuration.
    """
    # Base Paths (relative to project root)
    data_dir: str = "data"
    logs_dir: str = "data/logs"
    traces_dir: str = "data/traces"
    output_dir: str = "data/output"

    # Trace Subdirectories
    thought_traces_dir: str = "data/traces/thought"
    audit_traces_dir: str = "data/traces/audit"
    test_traces_dir: str = "data/traces/test"
    error_traces_dir: str = "data/traces/error"
    resource_traces_dir: str = "data/traces/resource"

    # State Persistence
    state_dir: str = "data/state"

    def get_absolute_path(self, relative_path: str, project_root: Optional[Path] = None) -> Path:
        """Convert relative path to absolute path."""
        if project_root is None:
            # Default: 4 levels up from this file
            project_root = Path(__file__).parent.parent.parent.parent
        return project_root / relative_path

    def ensure_directories_exist(self, project_root: Optional[Path] = None) -> None:
        """Create all configured directories if they don't exist."""
        dirs = [
            self.data_dir, self.logs_dir, self.traces_dir, self.output_dir,
            self.thought_traces_dir, self.audit_traces_dir, self.test_traces_dir,
            self.error_traces_dir, self.resource_traces_dir, self.state_dir,
        ]
        for dir_path in dirs:
            full_path = self.get_absolute_path(dir_path, project_root)
            full_path.mkdir(parents=True, exist_ok=True)


# ============================================================================
# BATCH PROCESSING CONFIGURATION
# ============================================================================

@dataclass
class BatchConfig:
    """
    Batch processing configuration.
    """
    max_workers: int = 4
    timeout_per_problem: float = 60.0
    max_files: int = 10000
    max_directory_depth: int = 10
    supported_extensions: List[str] = field(default_factory=lambda: [
        ".txt", ".json", ".csv", ".md", ".tex"
    ])
    watch_poll_interval: float = 5.0


# ============================================================================
# MAIN CONFIGURATION CLASS
# ============================================================================

@dataclass
class Config:
    """
    Main configuration container aggregating all subsystem configurations.

    This is the primary interface for accessing configuration values throughout
    the system.

    Example:
        config = get_config()

        # Access hardware config
        if config.hardware.can_load_llm():
            load_model()

        # Check thresholds
        if vram_usage > config.thresholds.vram_warning:
            logger.warning("VRAM usage high")

        # Get timeout
        timeout = config.timeouts.get_timeout("integration")
    """
    hardware: HardwareConfig = field(default_factory=HardwareConfig)
    thresholds: ResourceThresholds = field(default_factory=ResourceThresholds)
    timeouts: TimeoutConfig = field(default_factory=TimeoutConfig)
    agent_pool: AgentPoolConfig = field(default_factory=AgentPoolConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    paths: PathConfig = field(default_factory=PathConfig)
    batch: BatchConfig = field(default_factory=BatchConfig)

    def load_from_env(self) -> "Config":
        """
        Load configuration overrides from environment variables.

        Environment variable naming convention:
            SYMBO_<SECTION>_<KEY>=value

        Examples:
            SYMBO_HARDWARE_MAX_VRAM_GB=16.0
            SYMBO_THRESHOLDS_VRAM_WARNING=0.80
            SYMBO_TIMEOUTS_DEFAULT=120.0
        """
        prefix = "SYMBO_"

        for key, value in os.environ.items():
            if not key.startswith(prefix):
                continue

            parts = key[len(prefix):].lower().split("_", 1)
            if len(parts) != 2:
                continue

            section, attr = parts[0], parts[1]

            section_map = {
                "hardware": self.hardware,
                "thresholds": self.thresholds,
                "timeouts": self.timeouts,
                "agentpool": self.agent_pool,
                "monitoring": self.monitoring,
                "logging": self.logging,
                "paths": self.paths,
                "batch": self.batch,
            }

            if section not in section_map:
                continue

            config_section = section_map[section]

            if hasattr(config_section, attr):
                current_value = getattr(config_section, attr)
                try:
                    # Type coercion based on current value type
                    if isinstance(current_value, bool):
                        new_value = value.lower() in ("true", "1", "yes")
                    elif isinstance(current_value, int):
                        new_value = int(value)
                    elif isinstance(current_value, float):
                        new_value = float(value)
                    else:
                        new_value = value

                    setattr(config_section, attr, new_value)
                    logger.debug(f"Config override: {section}.{attr} = {new_value}")
                except (ValueError, TypeError) as e:
                    logger.warning(f"Failed to parse env var {key}={value}: {e}")

        return self

    def load_from_file(self, file_path: str) -> "Config":
        """
        Load configuration from YAML or JSON file.

        Args:
            file_path: Path to configuration file (.yaml, .yml, or .json)
        """
        path = Path(file_path)

        if not path.exists():
            logger.warning(f"Config file not found: {file_path}")
            return self

        try:
            with open(path, 'r') as f:
                if path.suffix in ('.yaml', '.yml'):
                    try:
                        import yaml
                        data = yaml.safe_load(f)
                    except ImportError:
                        logger.warning("PyYAML not installed, skipping YAML config")
                        return self
                else:
                    data = json.load(f)

            self._apply_dict(data)
            logger.info(f"Loaded configuration from {file_path}")

        except Exception as e:
            logger.error(f"Failed to load config file {file_path}: {e}")

        return self

    def _apply_dict(self, data: Dict[str, Any]) -> None:
        """Apply dictionary values to configuration."""
        section_map = {
            "hardware": self.hardware,
            "thresholds": self.thresholds,
            "timeouts": self.timeouts,
            "agent_pool": self.agent_pool,
            "monitoring": self.monitoring,
            "logging": self.logging,
            "paths": self.paths,
            "batch": self.batch,
        }

        for section_name, section_data in data.items():
            if section_name not in section_map:
                continue

            config_section = section_map[section_name]

            if isinstance(section_data, dict):
                for key, value in section_data.items():
                    if hasattr(config_section, key):
                        setattr(config_section, key, value)

    def validate(self) -> List[str]:
        """
        Validate all configuration values.

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        # Validate thresholds
        errors.extend(self.thresholds.validate())

        # Validate hardware
        if self.hardware.max_vram_gb <= 0:
            errors.append("max_vram_gb must be positive")
        if self.hardware.max_ram_gb <= 0:
            errors.append("max_ram_gb must be positive")
        if self.hardware.max_cpu_cores <= 0:
            errors.append("max_cpu_cores must be positive")

        # Validate timeouts
        for field_name in dir(self.timeouts):
            if field_name.startswith("_"):
                continue
            value = getattr(self.timeouts, field_name)
            if isinstance(value, (int, float)) and value <= 0:
                errors.append(f"Timeout {field_name} must be positive, got {value}")

        # Validate agent pool
        if self.agent_pool.max_active_agents <= 0:
            errors.append("max_active_agents must be positive")
        if self.agent_pool.max_cognitive_agents <= 0:
            errors.append("max_cognitive_agents must be positive")

        return errors

    def to_dict(self) -> Dict[str, Any]:
        """Export configuration as dictionary."""
        from dataclasses import asdict
        return {
            "hardware": asdict(self.hardware),
            "thresholds": asdict(self.thresholds),
            "timeouts": asdict(self.timeouts),
            "agent_pool": asdict(self.agent_pool),
            "monitoring": asdict(self.monitoring),
            "logging": asdict(self.logging),
            "paths": asdict(self.paths),
            "batch": asdict(self.batch),
        }

    def save_to_file(self, file_path: str) -> None:
        """Save current configuration to file."""
        path = Path(file_path)

        with open(path, 'w') as f:
            if path.suffix in ('.yaml', '.yml'):
                try:
                    import yaml
                    yaml.dump(self.to_dict(), f, default_flow_style=False)
                except ImportError:
                    # Fallback to JSON
                    json.dump(self.to_dict(), f, indent=2)
            else:
                json.dump(self.to_dict(), f, indent=2)

        logger.info(f"Saved configuration to {file_path}")


# ============================================================================
# SINGLETON CONFIGURATION INSTANCE
# ============================================================================

_config_instance: Optional[Config] = None


def get_config() -> Config:
    """
    Get the global configuration singleton.

    On first call, loads configuration from:
    1. Default values
    2. Environment variables (SYMBO_*)
    3. Config file (if SYMBO_CONFIG_FILE env var is set)

    Returns:
        Config: Global configuration instance
    """
    global _config_instance

    if _config_instance is None:
        _config_instance = Config()
        _config_instance.load_from_env()

        # Load from config file if specified
        config_file = os.environ.get("SYMBO_CONFIG_FILE")
        if config_file:
            _config_instance.load_from_file(config_file)

        # Validate
        errors = _config_instance.validate()
        if errors:
            for error in errors:
                logger.warning(f"Configuration validation error: {error}")

    return _config_instance


def reload_config() -> Config:
    """
    Force reload of configuration.

    Useful when environment variables or config files have changed.

    Returns:
        Config: Newly loaded configuration instance
    """
    global _config_instance
    _config_instance = None
    return get_config()


# ============================================================================
# EXAMPLE CONFIGURATION FILE TEMPLATE
# ============================================================================

CONFIG_FILE_TEMPLATE = """
# SYMBO_AGENTIC_REASONERS Configuration
# =====================================
# Copy this file to config.yaml and customize as needed.
# Set SYMBO_CONFIG_FILE=config.yaml to load.

hardware:
  max_vram_gb: 8.0
  llm_vram_requirement_gb: 5.5
  infrastructural_vram_gb: 0.5
  max_ram_gb: 32.0
  max_cpu_cores: 8

thresholds:
  vram_warning: 0.85
  vram_threshold: 0.90
  vram_critical: 0.95
  vram_emergency: 0.98
  ram_warning: 0.80
  ram_threshold: 0.85
  ram_critical: 0.92
  ram_emergency: 0.95
  cpu_warning: 0.80
  cpu_threshold: 0.90
  cpu_critical: 0.95
  disk_warning: 0.90
  disk_critical: 0.95

timeouts:
  default: 60.0
  llm_inference: 120.0
  symbolic_solve: 90.0
  integration: 180.0
  proof: 300.0
  search: 30.0
  message: 10.0

agent_pool:
  max_active_agents: 8
  max_parallel_workers: 4
  max_cognitive_agents: 1
  specialist_standby_timeout: 300.0
  supervisor_standby_timeout: 600.0

monitoring:
  watchdog_check_interval: 1.0
  ams_monitor_interval: 5.0
  resource_history_size: 12
  sustained_threshold_count: 3

logging:
  default_level: INFO
  log_to_file: true
  use_json_format: false
  trace_enabled: true

paths:
  data_dir: data
  logs_dir: data/logs
  traces_dir: data/traces
"""


if __name__ == "__main__":
    # Demo: Print default configuration
    config = get_config()

    print("=" * 60)
    print("SYMBO_AGENTIC_REASONERS Configuration")
    print("=" * 60)
    print()

    print("Hardware Configuration:")
    print(f"  Max VRAM: {config.hardware.max_vram_gb} GB")
    print(f"  Max RAM: {config.hardware.max_ram_gb} GB")
    print(f"  Max CPU Cores: {config.hardware.max_cpu_cores}")
    print(f"  Can Load LLM: {config.hardware.can_load_llm()}")
    print()

    print("Resource Thresholds:")
    print(f"  VRAM Warning: {config.thresholds.vram_warning * 100}%")
    print(f"  VRAM Critical: {config.thresholds.vram_critical * 100}%")
    print(f"  RAM Warning: {config.thresholds.ram_warning * 100}%")
    print()

    print("Timeout Configuration:")
    print(f"  Default: {config.timeouts.default}s")
    print(f"  Integration: {config.timeouts.integration}s")
    print(f"  Proof: {config.timeouts.proof}s")
    print()

    # Validate
    errors = config.validate()
    if errors:
        print("Validation Errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("Configuration is valid!")

    print()
    print("To generate config file template:")
    print("  python -c \"from symbo_agentic_reasoners.config.settings import CONFIG_FILE_TEMPLATE; print(CONFIG_FILE_TEMPLATE)\" > config.yaml")
