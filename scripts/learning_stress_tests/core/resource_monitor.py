"""
Real-time resource monitoring for long-running tests.

Tracks CPU, memory, threads, and disk I/O to detect leaks and bottlenecks.
"""

import psutil
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict
from pathlib import Path
import csv


@dataclass
class ResourceSnapshot:
    """Point-in-time resource usage snapshot"""
    timestamp: datetime
    memory_rss_mb: float
    memory_heap_mb: float
    cpu_percent: float
    thread_count: int
    disk_read_mb: float = 0.0
    disk_write_mb: float = 0.0

    def to_dict(self) -> Dict:
        return {
            'timestamp': self.timestamp.isoformat(),
            'memory_rss_mb': self.memory_rss_mb,
            'memory_heap_mb': self.memory_heap_mb,
            'cpu_percent': self.cpu_percent,
            'thread_count': self.thread_count,
            'disk_read_mb': self.disk_read_mb,
            'disk_write_mb': self.disk_write_mb
        }


class ResourceMonitor:
    """
    Continuous resource monitoring with anomaly detection.

    Runs in a background thread, sampling resource usage every 500ms.
    """

    def __init__(self, sampling_interval_ms: int = 500):
        self.sampling_interval_ms = sampling_interval_ms
        self.snapshots: List[ResourceSnapshot] = []
        self.alert_thresholds = {
            'memory_growth_mb_per_min': 100,  # Alert if >100MB/min growth
            'max_threads': 100,                # Alert if >100 threads
            'cpu_sustained_percent': 80,       # Alert if >80% CPU sustained
        }
        self._monitoring_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._process = psutil.Process()
        self._lock = threading.Lock()
        self._initial_io: Optional[psutil._common.pio] = None

    def start_monitoring(self):
        """Start the background monitoring thread"""
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            return  # Already running

        self._stop_event.clear()
        self._initial_io = self._process.io_counters()
        self._monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True,
            name="ResourceMonitor"
        )
        self._monitoring_thread.start()
        print("[ResourceMonitor] Monitoring started")

    def stop_monitoring(self):
        """Stop the background monitoring thread"""
        if not self._monitoring_thread:
            return

        self._stop_event.set()
        if self._monitoring_thread.is_alive():
            self._monitoring_thread.join(timeout=2.0)
        print("[ResourceMonitor] Monitoring stopped")

    def _monitoring_loop(self):
        """Main monitoring loop (runs in background thread)"""
        while not self._stop_event.is_set():
            snapshot = self.take_snapshot()
            with self._lock:
                self.snapshots.append(snapshot)

            # Sleep for sampling interval
            time.sleep(self.sampling_interval_ms / 1000.0)

    def take_snapshot(self) -> ResourceSnapshot:
        """Take a point-in-time snapshot of resource usage"""
        try:
            # Memory info
            mem_info = self._process.memory_info()
            memory_rss_mb = mem_info.rss / (1024 * 1024)

            # Try to get heap size (Python-specific memory)
            try:
                memory_heap_mb = mem_info.data / (1024 * 1024)
            except AttributeError:
                memory_heap_mb = memory_rss_mb  # Fallback

            # CPU usage
            cpu_percent = self._process.cpu_percent(interval=0.1)

            # Thread count
            thread_count = self._process.num_threads()

            # Disk I/O
            try:
                io_counters = self._process.io_counters()
                if self._initial_io:
                    disk_read_mb = (io_counters.read_bytes - self._initial_io.read_bytes) / (1024 * 1024)
                    disk_write_mb = (io_counters.write_bytes - self._initial_io.write_bytes) / (1024 * 1024)
                else:
                    disk_read_mb = disk_write_mb = 0.0
            except (AttributeError, psutil.AccessDenied):
                disk_read_mb = disk_write_mb = 0.0

            return ResourceSnapshot(
                timestamp=datetime.now(),
                memory_rss_mb=memory_rss_mb,
                memory_heap_mb=memory_heap_mb,
                cpu_percent=cpu_percent,
                thread_count=thread_count,
                disk_read_mb=disk_read_mb,
                disk_write_mb=disk_write_mb
            )
        except Exception as e:
            # Return zero snapshot on error
            return ResourceSnapshot(
                timestamp=datetime.now(),
                memory_rss_mb=0.0,
                memory_heap_mb=0.0,
                cpu_percent=0.0,
                thread_count=0
            )

    def detect_memory_leak(self, window_minutes: int = 5) -> Optional[float]:
        """
        Detect memory leaks using linear regression.

        Args:
            window_minutes: Time window to analyze

        Returns: Memory growth rate in MB/minute, or None if no leak detected
        """
        with self._lock:
            if not self.snapshots:
                return None

            # Get snapshots from last N minutes
            cutoff_time = datetime.now().timestamp() - (window_minutes * 60)
            recent_snapshots = [
                s for s in self.snapshots
                if s.timestamp.timestamp() >= cutoff_time
            ]

            if len(recent_snapshots) < 10:  # Need enough data points
                return None

        # Simple linear regression on memory over time
        times = [(s.timestamp.timestamp() - recent_snapshots[0].timestamp.timestamp()) / 60.0
                 for s in recent_snapshots]  # Minutes since start
        memories = [s.memory_rss_mb for s in recent_snapshots]

        n = len(times)
        sum_x = sum(times)
        sum_y = sum(memories)
        sum_xy = sum(t * m for t, m in zip(times, memories))
        sum_x2 = sum(t * t for t in times)

        # Slope of regression line (MB per minute)
        try:
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        except ZeroDivisionError:
            return None

        # Only report if significant leak (>threshold)
        if slope > self.alert_thresholds['memory_growth_mb_per_min']:
            return slope
        return None

    def detect_thread_explosion(self) -> bool:
        """
        Detect if thread count exceeds safe threshold.

        Returns: True if thread explosion detected
        """
        with self._lock:
            if not self.snapshots:
                return False

            latest = self.snapshots[-1]
            return latest.thread_count > self.alert_thresholds['max_threads']

    def detect_cpu_saturation(self, window_minutes: int = 2) -> bool:
        """
        Detect sustained high CPU usage.

        Args:
            window_minutes: Window to check for sustained high CPU

        Returns: True if CPU >threshold for entire window
        """
        with self._lock:
            if not self.snapshots:
                return False

            cutoff_time = datetime.now().timestamp() - (window_minutes * 60)
            recent_snapshots = [
                s for s in self.snapshots
                if s.timestamp.timestamp() >= cutoff_time
            ]

            if len(recent_snapshots) < 5:
                return False

        threshold = self.alert_thresholds['cpu_sustained_percent']
        return all(s.cpu_percent > threshold for s in recent_snapshots)

    def get_peak_usage(self) -> ResourceSnapshot:
        """Get the peak resource usage snapshot"""
        with self._lock:
            if not self.snapshots:
                return ResourceSnapshot(
                    timestamp=datetime.now(),
                    memory_rss_mb=0.0,
                    memory_heap_mb=0.0,
                    cpu_percent=0.0,
                    thread_count=0
                )

            # Peak is snapshot with highest memory
            return max(self.snapshots, key=lambda s: s.memory_rss_mb)

    def get_average_usage(self, last_n_minutes: int = 5) -> ResourceSnapshot:
        """
        Get average resource usage over last N minutes.

        Args:
            last_n_minutes: Time window to average over

        Returns: Snapshot with averaged values
        """
        with self._lock:
            if not self.snapshots:
                return ResourceSnapshot(
                    timestamp=datetime.now(),
                    memory_rss_mb=0.0,
                    memory_heap_mb=0.0,
                    cpu_percent=0.0,
                    thread_count=0
                )

            cutoff_time = datetime.now().timestamp() - (last_n_minutes * 60)
            recent_snapshots = [
                s for s in self.snapshots
                if s.timestamp.timestamp() >= cutoff_time
            ]

            if not recent_snapshots:
                recent_snapshots = self.snapshots

        n = len(recent_snapshots)
        return ResourceSnapshot(
            timestamp=datetime.now(),
            memory_rss_mb=sum(s.memory_rss_mb for s in recent_snapshots) / n,
            memory_heap_mb=sum(s.memory_heap_mb for s in recent_snapshots) / n,
            cpu_percent=sum(s.cpu_percent for s in recent_snapshots) / n,
            thread_count=int(sum(s.thread_count for s in recent_snapshots) / n),
            disk_read_mb=sum(s.disk_read_mb for s in recent_snapshots) / n,
            disk_write_mb=sum(s.disk_write_mb for s in recent_snapshots) / n
        )

    def export_timeline(self, path: Path):
        """
        Export resource timeline to CSV for visualization.

        Args:
            path: Path to CSV file
        """
        with self._lock:
            snapshots_copy = self.snapshots.copy()

        with open(path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'timestamp', 'memory_rss_mb', 'memory_heap_mb',
                'cpu_percent', 'thread_count', 'disk_read_mb', 'disk_write_mb'
            ])

            for snapshot in snapshots_copy:
                writer.writerow([
                    snapshot.timestamp.isoformat(),
                    f"{snapshot.memory_rss_mb:.2f}",
                    f"{snapshot.memory_heap_mb:.2f}",
                    f"{snapshot.cpu_percent:.1f}",
                    snapshot.thread_count,
                    f"{snapshot.disk_read_mb:.2f}",
                    f"{snapshot.disk_write_mb:.2f}"
                ])

        print(f"[ResourceMonitor] Timeline exported to {path}")

    def get_summary(self) -> Dict:
        """Get a summary of resource usage"""
        peak = self.get_peak_usage()
        avg = self.get_average_usage()
        memory_leak_rate = self.detect_memory_leak()
        thread_explosion = self.detect_thread_explosion()
        cpu_saturation = self.detect_cpu_saturation()

        with self._lock:
            snapshot_count = len(self.snapshots)
            duration_minutes = 0.0
            if self.snapshots:
                duration = self.snapshots[-1].timestamp - self.snapshots[0].timestamp
                duration_minutes = duration.total_seconds() / 60.0

        return {
            'duration_minutes': duration_minutes,
            'snapshot_count': snapshot_count,
            'peak_memory_mb': peak.memory_rss_mb,
            'avg_memory_mb': avg.memory_rss_mb,
            'peak_cpu_percent': peak.cpu_percent,
            'avg_cpu_percent': avg.cpu_percent,
            'peak_threads': peak.thread_count,
            'avg_threads': avg.thread_count,
            'total_disk_read_mb': peak.disk_read_mb,
            'total_disk_write_mb': peak.disk_write_mb,
            'memory_leak_detected': memory_leak_rate is not None,
            'memory_leak_rate_mb_per_min': memory_leak_rate if memory_leak_rate else 0.0,
            'thread_explosion_detected': thread_explosion,
            'cpu_saturation_detected': cpu_saturation
        }
