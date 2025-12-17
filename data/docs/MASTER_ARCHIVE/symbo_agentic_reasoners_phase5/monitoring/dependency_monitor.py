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
Dependency Monitor for SYMBO_AGENTIC_REASONERS Phase 5
====================================

Monitors availability and health of critical dependencies in production,
with special focus on PyTorch/CUDA availability for neural components.

This module addresses the audit recommendation:
"Monitor PyTorch availability in production deployments"

Usage:
    from symbo_agentic_reasoners_phase5.monitoring import DependencyMonitor, get_dependency_report

    # Quick check
    report = get_dependency_report()
    print(report)

    # Full monitoring
    monitor = DependencyMonitor()
    monitor.start_monitoring(interval_seconds=60)
    ...
    monitor.stop_monitoring()
"""

import os
import sys
import logging
import threading
import time
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from enum import Enum

# Configure logger
logger = logging.getLogger('symbo_agentic_reasoners.phase5.monitoring')


class DependencyStatus(Enum):
    """Status of a dependency"""
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    DEGRADED = "degraded"  # Available but with reduced functionality
    UNKNOWN = "unknown"


@dataclass
class DependencyInfo:
    """Information about a single dependency"""
    name: str
    status: DependencyStatus
    version: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    checked_at: datetime = field(default_factory=datetime.now)
    warning_message: Optional[str] = None


def check_pytorch_availability() -> DependencyInfo:
    """
    Check PyTorch availability and CUDA support.

    Returns:
        DependencyInfo with PyTorch status and CUDA details
    """
    try:
        import torch

        # Basic info
        torch_version = torch.__version__
        cuda_available = torch.cuda.is_available()

        details = {
            'version': torch_version,
            'cuda_available': cuda_available,
            'cuda_version': None,
            'device_count': 0,
            'current_device': None,
            'device_name': None,
            'memory_allocated': None,
            'memory_reserved': None
        }

        if cuda_available:
            details['cuda_version'] = torch.version.cuda
            details['device_count'] = torch.cuda.device_count()
            details['current_device'] = torch.cuda.current_device()
            details['device_name'] = torch.cuda.get_device_name(0)

            # Memory info (in MB)
            details['memory_allocated'] = torch.cuda.memory_allocated(0) / (1024 ** 2)
            details['memory_reserved'] = torch.cuda.memory_reserved(0) / (1024 ** 2)

            return DependencyInfo(
                name='pytorch',
                status=DependencyStatus.AVAILABLE,
                version=torch_version,
                details=details
            )
        else:
            # PyTorch available but no CUDA
            return DependencyInfo(
                name='pytorch',
                status=DependencyStatus.DEGRADED,
                version=torch_version,
                details=details,
                warning_message=(
                    "PyTorch is available but CUDA is not. "
                    "Neural components will run on CPU (slower). "
                    "Consider installing CUDA-enabled PyTorch for better performance."
                )
            )

    except ImportError:
        return DependencyInfo(
            name='pytorch',
            status=DependencyStatus.UNAVAILABLE,
            details={'error': 'PyTorch not installed'},
            warning_message=(
                "PyTorch is not installed. Neural components (SymboLLMCore, training) "
                "will use fallback symbolic methods. To enable neural features: "
                "pip install torch (or pip install torch --index-url https://download.pytorch.org/whl/cu118 for CUDA)"
            )
        )
    except Exception as e:
        return DependencyInfo(
            name='pytorch',
            status=DependencyStatus.UNKNOWN,
            details={'error': str(e)},
            warning_message=f"Error checking PyTorch: {e}"
        )


def check_sympy_availability() -> DependencyInfo:
    """Check SymPy availability"""
    try:
        import sympy
        return DependencyInfo(
            name='sympy',
            status=DependencyStatus.AVAILABLE,
            version=sympy.__version__
        )
    except ImportError:
        return DependencyInfo(
            name='sympy',
            status=DependencyStatus.UNAVAILABLE,
            warning_message="SymPy is required for symbolic computation. Install with: pip install sympy"
        )


def check_numpy_availability() -> DependencyInfo:
    """Check NumPy availability"""
    try:
        import numpy as np
        return DependencyInfo(
            name='numpy',
            status=DependencyStatus.AVAILABLE,
            version=np.__version__
        )
    except ImportError:
        return DependencyInfo(
            name='numpy',
            status=DependencyStatus.UNAVAILABLE,
            warning_message="NumPy is required. Install with: pip install numpy"
        )


def check_matplotlib_availability() -> DependencyInfo:
    """Check Matplotlib availability for visualization exports"""
    try:
        import matplotlib
        return DependencyInfo(
            name='matplotlib',
            status=DependencyStatus.AVAILABLE,
            version=matplotlib.__version__
        )
    except ImportError:
        return DependencyInfo(
            name='matplotlib',
            status=DependencyStatus.UNAVAILABLE,
            warning_message=(
                "Matplotlib not available. Visualization exports (plot_contour, plot_surface) "
                "will not work. Install with: pip install matplotlib"
            )
        )


def check_networkx_availability() -> DependencyInfo:
    """Check NetworkX availability for knowledge base"""
    try:
        import networkx as nx
        return DependencyInfo(
            name='networkx',
            status=DependencyStatus.AVAILABLE,
            version=nx.__version__
        )
    except ImportError:
        return DependencyInfo(
            name='networkx',
            status=DependencyStatus.UNAVAILABLE,
            warning_message="NetworkX not available. KnowledgeBase will use fallback dict storage."
        )


def check_scikit_optimize_availability() -> DependencyInfo:
    """Check scikit-optimize availability"""
    try:
        import skopt
        return DependencyInfo(
            name='scikit-optimize',
            status=DependencyStatus.AVAILABLE,
            version=skopt.__version__
        )
    except ImportError:
        return DependencyInfo(
            name='scikit-optimize',
            status=DependencyStatus.UNAVAILABLE,
            warning_message="scikit-optimize not available. symbolic_regression will use fallback."
        )


def get_dependency_report() -> Dict[str, Any]:
    """
    Generate a comprehensive dependency availability report.

    Returns:
        Dictionary with all dependency statuses and recommendations
    """
    dependencies = [
        check_pytorch_availability(),
        check_sympy_availability(),
        check_numpy_availability(),
        check_matplotlib_availability(),
        check_networkx_availability(),
        check_scikit_optimize_availability(),
    ]

    report = {
        'generated_at': datetime.now().isoformat(),
        'python_version': sys.version,
        'platform': sys.platform,
        'dependencies': {},
        'warnings': [],
        'critical_missing': [],
        'optional_missing': []
    }

    critical_deps = {'sympy', 'numpy'}

    for dep in dependencies:
        report['dependencies'][dep.name] = {
            'status': dep.status.value,
            'version': dep.version,
            'details': dep.details,
            'checked_at': dep.checked_at.isoformat()
        }

        if dep.warning_message:
            report['warnings'].append({
                'dependency': dep.name,
                'message': dep.warning_message
            })

        if dep.status == DependencyStatus.UNAVAILABLE:
            if dep.name in critical_deps:
                report['critical_missing'].append(dep.name)
            else:
                report['optional_missing'].append(dep.name)

    # Overall health assessment
    if report['critical_missing']:
        report['health'] = 'CRITICAL'
        report['health_message'] = f"Critical dependencies missing: {report['critical_missing']}"
    elif 'pytorch' in [d.name for d in dependencies if d.status != DependencyStatus.AVAILABLE]:
        report['health'] = 'DEGRADED'
        report['health_message'] = "PyTorch unavailable - neural features disabled"
    elif report['optional_missing']:
        report['health'] = 'FUNCTIONAL'
        report['health_message'] = f"Functional with optional features disabled: {report['optional_missing']}"
    else:
        report['health'] = 'HEALTHY'
        report['health_message'] = "All dependencies available"

    return report


def log_dependency_status(level: int = logging.INFO):
    """
    Log dependency status at specified level.

    Args:
        level: Logging level (default: INFO)
    """
    report = get_dependency_report()

    logger.log(level, f"Dependency Health: {report['health']}")
    logger.log(level, f"Message: {report['health_message']}")

    # Log warnings
    for warning in report['warnings']:
        if 'pytorch' in warning['dependency'].lower():
            logger.warning(f"[{warning['dependency']}] {warning['message']}")
        else:
            logger.info(f"[{warning['dependency']}] {warning['message']}")

    # Log PyTorch details specifically
    pytorch_info = report['dependencies'].get('pytorch', {})
    if pytorch_info.get('status') == 'available':
        details = pytorch_info.get('details', {})
        if details.get('cuda_available'):
            logger.info(
                f"PyTorch {pytorch_info.get('version')} with CUDA {details.get('cuda_version')} "
                f"on {details.get('device_name')}"
            )
        else:
            logger.warning(
                f"PyTorch {pytorch_info.get('version')} running on CPU only"
            )


class DependencyMonitor:
    """
    Continuous dependency monitoring for production deployments.

    Periodically checks dependency availability and logs changes.
    Useful for detecting runtime issues like GPU memory exhaustion.
    """

    def __init__(
        self,
        check_interval: float = 60.0,
        on_status_change: Optional[Callable[[str, DependencyStatus, DependencyStatus], None]] = None
    ):
        """
        Initialize the dependency monitor.

        Args:
            check_interval: Seconds between checks (default: 60)
            on_status_change: Callback when dependency status changes
        """
        self.check_interval = check_interval
        self.on_status_change = on_status_change

        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._last_status: Dict[str, DependencyStatus] = {}
        self._check_count = 0

        # Initialize with current status
        self._update_status()

    def _update_status(self):
        """Update dependency status and detect changes"""
        report = get_dependency_report()

        for name, info in report['dependencies'].items():
            current_status = DependencyStatus(info['status'])
            previous_status = self._last_status.get(name)

            if previous_status is not None and current_status != previous_status:
                logger.warning(
                    f"Dependency status change: {name} {previous_status.value} -> {current_status.value}"
                )
                if self.on_status_change:
                    self.on_status_change(name, previous_status, current_status)

            self._last_status[name] = current_status

        self._check_count += 1

    def _monitor_loop(self):
        """Background monitoring loop"""
        while self._running:
            try:
                self._update_status()
            except Exception as e:
                logger.error(f"Error in dependency monitor: {e}")

            time.sleep(self.check_interval)

    def start_monitoring(self, interval_seconds: float = None):
        """
        Start background monitoring.

        Args:
            interval_seconds: Override check interval
        """
        if self._running:
            logger.warning("Monitor already running")
            return

        if interval_seconds:
            self.check_interval = interval_seconds

        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()

        logger.info(f"Dependency monitor started (interval: {self.check_interval}s)")

    def stop_monitoring(self):
        """Stop background monitoring"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5.0)
            self._thread = None

        logger.info("Dependency monitor stopped")

    def get_current_status(self) -> Dict[str, DependencyStatus]:
        """Get current dependency status"""
        return self._last_status.copy()

    def get_statistics(self) -> Dict[str, Any]:
        """Get monitoring statistics"""
        return {
            'running': self._running,
            'check_interval': self.check_interval,
            'check_count': self._check_count,
            'current_status': {k: v.value for k, v in self._last_status.items()}
        }


# Module-level initialization: log status on import
def _init_logging():
    """Initialize dependency logging on module import"""
    try:
        log_dependency_status(logging.DEBUG)
    except Exception:
        pass  # Silently ignore logging errors during import


# Run initialization
_init_logging()
