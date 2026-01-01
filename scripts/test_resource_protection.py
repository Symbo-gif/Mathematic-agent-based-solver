#!/usr/bin/env python
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
Test script for resource protection systems

Tests:
1. AMS emergency shutdown and monitoring
2. Watchdog timeout system
3. ResourceGovernor integration

Usage:
    python scripts/test_resource_protection.py
"""

import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def test_ams():
    """Test Agent Management System resource monitoring"""
    print("\n" + "=" * 60)
    print("TEST: AMS Resource Monitoring")
    print("=" * 60)

    from symbo_agentic_reasoners.infrastructure import (
        AgentManagementSystem, EmergencyLevel
    )

    ams = AgentManagementSystem()
    ams.start()

    try:
        # Get resource metrics
        snapshot = ams.get_resource_snapshot()
        print(f"\nResource Snapshot:")
        print(f"  VRAM:  {snapshot['vram_utilization']:.1%} ({snapshot['vram_gb']:.1f} GB)")
        print(f"  RAM:   {snapshot['ram_utilization']:.1%}")
        print(f"  CPU:   {snapshot['cpu_utilization']:.1%}")
        print(f"  Emergency Level: {snapshot['emergency_level']}")
        print(f"  Throttled: {snapshot['throttled']}")

        # Check statistics
        stats = ams.get_statistics()
        print(f"\nAMS Statistics:")
        print(f"  psutil available: {stats['psutil_available']}")
        print(f"  Total agents: {stats['total_agents']}")
        print(f"  Can activate cognitive: {stats['can_activate_cognitive']}")

        # Test emergency level getter
        level = ams.get_emergency_level()
        assert level in EmergencyLevel, "Emergency level should be valid enum"
        print(f"\n[OK] AMS test passed")
        return True

    except Exception as e:
        print(f"\n[FAIL] AMS test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        ams.stop()


def test_watchdog():
    """Test Watchdog timeout system"""
    print("\n" + "=" * 60)
    print("TEST: Watchdog Timeout System")
    print("=" * 60)

    from symbo_agentic_reasoners.infrastructure import (
        Watchdog, get_watchdog, TaskStatus, with_timeout
    )

    watchdog = get_watchdog()
    watchdog.start()

    try:
        # Test task lifecycle
        print("\n1. Task lifecycle test:")
        task_id = watchdog.start_task(
            "lifecycle_test",
            timeout=30,
            description="Lifecycle test task"
        )
        print(f"   Started: {task_id}")

        status = watchdog.get_task_status(task_id)
        assert status['status'] == 'running', "Task should be running"
        print(f"   Status: {status['status']}")

        watchdog.heartbeat(task_id)
        print("   Heartbeat sent")

        watchdog.complete_task(task_id)
        print("   Completed")

        # Test decorator
        print("\n2. Decorator test:")

        @with_timeout(10)
        def quick_operation():
            time.sleep(0.1)
            return "success"

        result = quick_operation()
        assert result == "success", "Decorated function should return result"
        print(f"   Decorated function returned: {result}")

        # Test context manager
        print("\n3. Context manager test:")
        with watchdog.timeout_context(10, "context_test") as ctx_id:
            time.sleep(0.1)
            print(f"   Inside context: {ctx_id}")
        print("   Context completed")

        # Statistics
        stats = watchdog.get_statistics()
        print(f"\nWatchdog Statistics:")
        print(f"   Tasks started: {stats['tasks_started']}")
        print(f"   Tasks completed: {stats['tasks_completed']}")
        print(f"   Timeout rate: {stats['timeout_rate']}%")

        print(f"\n[OK] Watchdog test passed")
        return True

    except Exception as e:
        print(f"\n[FAIL] Watchdog test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        watchdog.stop()


def test_resource_governor():
    """Test ResourceGovernor integration"""
    print("\n" + "=" * 60)
    print("TEST: ResourceGovernor Integration")
    print("=" * 60)

    from symbo_agentic_reasoners.infrastructure import (
        ResourceGovernor, get_governor, ThrottleLevel
    )

    governor = get_governor()
    governor.initialize()
    governor.start()

    try:
        # Get status
        print("\n1. Resource Status:")
        status = governor.get_status()
        print(f"   VRAM:     {status.vram_utilization:.1%}")
        print(f"   RAM:      {status.ram_utilization:.1%}")
        print(f"   CPU:      {status.cpu_utilization:.1%}")
        print(f"   Disk:     {status.disk_utilization:.1%}")
        print(f"   Emergency: {status.emergency_level.name}")
        print(f"   Throttle:  {status.throttle_level.name}")
        print(f"   Can proceed: {status.can_proceed}")

        # Test operation flow
        print("\n2. Operation Flow:")
        can = governor.can_proceed()
        print(f"   Can proceed: {can}")

        task_id = governor.request_operation(
            operation_type="test",
            timeout=30,
            description="Test operation"
        )
        if task_id:
            print(f"   Operation approved")
            governor.heartbeat(task_id)
            print("   Heartbeat sent")
            governor.complete_operation(task_id, success=True)
            print("   Operation completed")
        else:
            print("   Operation blocked (system may be stressed)")

        # Test warnings
        print("\n3. Warnings:")
        if status.warnings:
            for w in status.warnings:
                print(f"   - {w}")
        else:
            print("   No warnings")

        # Statistics
        stats = governor.get_statistics()
        print(f"\nGovernor Statistics:")
        print(f"   Operations allowed: {stats['operations_allowed']}")
        print(f"   Operations throttled: {stats['operations_throttled']}")
        print(f"   Operations blocked: {stats['operations_blocked']}")

        print(f"\n[OK] ResourceGovernor test passed")
        return True

    except Exception as e:
        print(f"\n[FAIL] ResourceGovernor test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        governor.stop()


def main():
    """Run all resource protection tests"""
    print("=" * 60)
    print("RESOURCE PROTECTION SYSTEM TESTS")
    print("=" * 60)

    results = []

    results.append(("AMS", test_ams()))
    results.append(("Watchdog", test_watchdog()))
    results.append(("ResourceGovernor", test_resource_governor()))

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    all_passed = True
    for name, passed in results:
        status = "[OK]" if passed else "[FAIL]"
        print(f"  {status} {name}")
        if not passed:
            all_passed = False

    print()
    if all_passed:
        print("All tests PASSED")
        return 0
    else:
        print("Some tests FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
