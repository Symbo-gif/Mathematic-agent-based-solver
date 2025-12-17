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
Hardware Detector - Dynamic Resource Detection
===============================================

Detects actual system resources at runtime instead of using hardcoded values.
This enables SYMBO to adapt to different hardware configurations.

Key Insight:
-----------
Symbolic agents (SymPy-based) run on CPU and can run in parallel.
Only SymboLLM training/inference requires GPU VRAM.

This means:
- Multiple specialists CAN run concurrently (CPU-bound)
- SymboLLM training is the only VRAM constraint
- RAM is the limit for number of concurrent agents
"""

import subprocess
import logging
from dataclasses import dataclass
from typing import Optional, Tuple

logger = logging.getLogger('symbo_agentic_reasoners.infrastructure.hardware_detector')

# Try to import psutil for system monitoring
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


@dataclass
class HardwareProfile:
    """Detected hardware capabilities"""
    # GPU
    gpu_name: str = "Unknown"
    vram_total_gb: float = 0.0
    vram_available_gb: float = 0.0
    has_cuda: bool = False

    # CPU
    cpu_name: str = "Unknown"
    cpu_cores: int = 1
    cpu_threads: int = 1

    # RAM
    ram_total_gb: float = 8.0
    ram_available_gb: float = 4.0

    # Derived limits
    max_parallel_symbolic_agents: int = 4
    can_train_symbo_llm: bool = False
    symbo_llm_vram_required: float = 5.5  # GB for 7B model quantized

    def __str__(self) -> str:
        return (
            f"HardwareProfile(\n"
            f"  GPU: {self.gpu_name} ({self.vram_total_gb:.1f}GB VRAM, {self.vram_available_gb:.1f}GB free)\n"
            f"  CPU: {self.cpu_name} ({self.cpu_cores} cores, {self.cpu_threads} threads)\n"
            f"  RAM: {self.ram_total_gb:.1f}GB total, {self.ram_available_gb:.1f}GB available\n"
            f"  Max parallel symbolic agents: {self.max_parallel_symbolic_agents}\n"
            f"  Can train SymboLLM: {self.can_train_symbo_llm}\n"
            f")"
        )


class HardwareDetector:
    """
    Detects and monitors system hardware resources.

    Usage:
        detector = HardwareDetector()
        profile = detector.detect()

        if profile.can_train_symbo_llm:
            # Safe to do GPU training
            pass

        # Always safe to run this many symbolic agents in parallel
        max_agents = profile.max_parallel_symbolic_agents
    """

    def __init__(self):
        self._cached_profile: Optional[HardwareProfile] = None

    def detect(self, refresh: bool = False) -> HardwareProfile:
        """
        Detect hardware capabilities.

        Args:
            refresh: Force re-detection even if cached

        Returns:
            HardwareProfile with detected capabilities
        """
        if self._cached_profile is not None and not refresh:
            # Update dynamic values (available memory)
            self._update_available_memory(self._cached_profile)
            return self._cached_profile

        profile = HardwareProfile()

        # Detect GPU
        self._detect_gpu(profile)

        # Detect CPU
        self._detect_cpu(profile)

        # Detect RAM
        self._detect_ram(profile)

        # Calculate derived limits
        self._calculate_limits(profile)

        self._cached_profile = profile
        logger.info(f"Hardware detected: {profile}")

        return profile

    def _detect_gpu(self, profile: HardwareProfile) -> None:
        """Detect GPU via nvidia-smi"""
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=name,memory.total,memory.free', '--format=csv,noheader,nounits'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0 and result.stdout.strip():
                lines = result.stdout.strip().split('\n')
                if lines:
                    parts = lines[0].split(',')
                    if len(parts) >= 3:
                        profile.gpu_name = parts[0].strip()
                        profile.vram_total_gb = float(parts[1].strip()) / 1024  # MB to GB
                        profile.vram_available_gb = float(parts[2].strip()) / 1024
                        profile.has_cuda = True
                        logger.info(f"Detected GPU: {profile.gpu_name} with {profile.vram_total_gb:.1f}GB VRAM")
        except FileNotFoundError:
            logger.info("nvidia-smi not found - no NVIDIA GPU detected")
        except subprocess.TimeoutExpired:
            logger.warning("nvidia-smi timed out")
        except Exception as e:
            logger.warning(f"GPU detection failed: {e}")

    def _detect_cpu(self, profile: HardwareProfile) -> None:
        """Detect CPU info"""
        if HAS_PSUTIL:
            try:
                profile.cpu_cores = psutil.cpu_count(logical=False) or 1
                profile.cpu_threads = psutil.cpu_count(logical=True) or 1

                # Try to get CPU name on Windows
                try:
                    import platform
                    profile.cpu_name = platform.processor() or "Unknown"
                except Exception:
                    pass

                logger.info(f"Detected CPU: {profile.cpu_cores} cores, {profile.cpu_threads} threads")
            except Exception as e:
                logger.warning(f"CPU detection failed: {e}")
        else:
            # Fallback
            import os
            profile.cpu_threads = os.cpu_count() or 1
            profile.cpu_cores = max(1, profile.cpu_threads // 2)

    def _detect_ram(self, profile: HardwareProfile) -> None:
        """Detect RAM info"""
        if HAS_PSUTIL:
            try:
                mem = psutil.virtual_memory()
                profile.ram_total_gb = mem.total / (1024 ** 3)
                profile.ram_available_gb = mem.available / (1024 ** 3)
                logger.info(f"Detected RAM: {profile.ram_total_gb:.1f}GB total, {profile.ram_available_gb:.1f}GB available")
            except Exception as e:
                logger.warning(f"RAM detection failed: {e}")

    def _update_available_memory(self, profile: HardwareProfile) -> None:
        """Update just the available memory values (for cached profiles)"""
        # Update RAM
        if HAS_PSUTIL:
            try:
                mem = psutil.virtual_memory()
                profile.ram_available_gb = mem.available / (1024 ** 3)
            except Exception:
                pass

        # Update VRAM
        if profile.has_cuda:
            try:
                result = subprocess.run(
                    ['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0 and result.stdout.strip():
                    profile.vram_available_gb = float(result.stdout.strip().split('\n')[0]) / 1024
            except Exception:
                pass

    def _calculate_limits(self, profile: HardwareProfile) -> None:
        """Calculate derived limits based on detected hardware"""

        # Symbolic agents are CPU-bound
        # Each agent uses ~100-500MB RAM when active
        # Conservative estimate: 500MB per agent
        ram_per_agent_gb = 0.5
        ram_for_system_gb = 4.0  # Reserve for OS and other processes

        usable_ram = max(0, profile.ram_available_gb - ram_for_system_gb)
        profile.max_parallel_symbolic_agents = max(1, int(usable_ram / ram_per_agent_gb))

        # Cap at CPU threads (no point having more agents than threads)
        profile.max_parallel_symbolic_agents = min(
            profile.max_parallel_symbolic_agents,
            profile.cpu_threads
        )

        # SymboLLM training needs GPU
        profile.symbo_llm_vram_required = 5.5  # 7B model quantized to 4-bit
        profile.can_train_symbo_llm = (
            profile.has_cuda and
            profile.vram_available_gb >= profile.symbo_llm_vram_required
        )

    def get_vram_status(self) -> Tuple[float, float]:
        """
        Get current VRAM usage.

        Returns:
            (used_gb, total_gb)
        """
        profile = self.detect()
        used = profile.vram_total_gb - profile.vram_available_gb
        return (used, profile.vram_total_gb)

    def get_ram_status(self) -> Tuple[float, float]:
        """
        Get current RAM usage.

        Returns:
            (used_gb, total_gb)
        """
        profile = self.detect(refresh=True)
        used = profile.ram_total_gb - profile.ram_available_gb
        return (used, profile.ram_total_gb)

    def can_spawn_symbolic_agent(self) -> bool:
        """Check if we have resources to spawn another symbolic agent"""
        profile = self.detect(refresh=True)
        # Need at least 500MB free RAM
        return profile.ram_available_gb >= 0.5

    def can_start_symbo_training(self) -> bool:
        """Check if we have resources to start SymboLLM training"""
        profile = self.detect(refresh=True)
        return profile.can_train_symbo_llm


# Singleton instance
_detector: Optional[HardwareDetector] = None


def get_hardware_detector() -> HardwareDetector:
    """Get or create the global hardware detector"""
    global _detector
    if _detector is None:
        _detector = HardwareDetector()
    return _detector


def detect_hardware() -> HardwareProfile:
    """Convenience function to detect hardware"""
    return get_hardware_detector().detect()


if __name__ == "__main__":
    """Test hardware detection"""
    print("=" * 60)
    print("HARDWARE DETECTION TEST")
    print("=" * 60)

    detector = HardwareDetector()
    profile = detector.detect()

    print()
    print(profile)
    print()

    print(f"Can spawn symbolic agent: {detector.can_spawn_symbolic_agent()}")
    print(f"Can train SymboLLM: {detector.can_start_symbo_training()}")

    vram_used, vram_total = detector.get_vram_status()
    print(f"VRAM: {vram_used:.1f}GB / {vram_total:.1f}GB used")

    ram_used, ram_total = detector.get_ram_status()
    print(f"RAM: {ram_used:.1f}GB / {ram_total:.1f}GB used")
