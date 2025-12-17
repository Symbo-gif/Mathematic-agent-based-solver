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
Advanced Injection Attack Tests
================================

Tests for sophisticated injection attacks including:
- Unicode homoglyph attacks
- Indirect import via string manipulation
- Format string exploitation
- Null byte injection
- Encoding-based bypasses
"""

import pytest
from symbo_agentic_reasoners.core.safe_parser import safe_parse, SecurityError


class TestUnicodeHomoglyphAttacks:
    """Test Unicode homoglyph attack prevention."""

    def test_cyrillic_import_blocked(self):
        """Cyrillic characters that look like Latin should be blocked."""
        # Cyrillic 'і' instead of Latin 'i'
        homoglyph_import = "__іmport__('os')"

        with pytest.raises((SecurityError, ValueError, SyntaxError)):
            safe_parse(homoglyph_import)

    def test_cyrillic_exec_blocked(self):
        """Cyrillic 'е' looks like Latin 'e'."""
        homoglyph_exec = "еxec('code')"

        with pytest.raises((SecurityError, ValueError, SyntaxError)):
            safe_parse(homoglyph_exec)

    def test_cyrillic_open_blocked(self):
        """Mixed Cyrillic/Latin script."""
        homoglyph_open = "opеn('/etc/passwd')"

        with pytest.raises((SecurityError, ValueError, SyntaxError)):
            safe_parse(homoglyph_open)

    def test_zero_width_characters_rejected(self):
        """Zero-width spaces should be rejected."""
        zero_width_attacks = [
            "x\u200b + 1",     # Zero-width space
            "x\u200c + 1",     # Zero-width non-joiner
            "x\u200d + 1",     # Zero-width joiner
            "x\ufeff + 1",     # Byte order mark (BOM)
        ]

        for attack in zero_width_attacks:
            # Should either be rejected or stripped
            try:
                result = safe_parse(attack)
                # If accepted, verify no zero-width chars remain
                assert '\u200b' not in str(result)
                assert '\u200c' not in str(result)
                assert '\u200d' not in str(result)
                assert '\ufeff' not in str(result)
            except (SecurityError, ValueError):
                # Rejection is acceptable
                pass


class TestIndirectImportAttacks:
    """Test indirect import attempts."""

    def test_getattr_builtins_import(self):
        """Indirect import via getattr on __builtins__."""
        with pytest.raises((SecurityError, NameError, KeyError, AttributeError)):
            safe_parse("getattr(__builtins__, '__im' + 'port__')('os')")

    def test_globals_import(self):
        """Import via globals() access."""
        with pytest.raises((SecurityError, NameError, KeyError)):
            safe_parse("globals()['__builtins__']['__import__']('os')")

    def test_vars_builtins_eval(self):
        """eval() via vars(__builtins__)."""
        with pytest.raises((SecurityError, NameError, KeyError)):
            safe_parse("vars(__builtins__)['eval']('1+1')")

    def test_string_concatenation_import(self):
        """Import via string concatenation to bypass pattern matching."""
        with pytest.raises((SecurityError, NameError, SyntaxError)):
            safe_parse("__im" + "port__('os')")


class TestFormatStringExploitation:
    """Test format string attack prevention."""

    def test_mro_access_blocked(self):
        """Access to __mro__ should be blocked."""
        with pytest.raises((SecurityError, ValueError, AttributeError, KeyError)):
            safe_parse("{0.__class__.__mro__[1].__subclasses__()}")

    def test_globals_via_format_blocked(self):
        """Accessing __globals__ via format string."""
        with pytest.raises((SecurityError, ValueError, AttributeError, KeyError)):
            safe_parse("{x.__globals__}")

    def test_format_class_access_blocked(self):
        """Class access via format string."""
        with pytest.raises((SecurityError, ValueError, AttributeError)):
            safe_parse("{}.format(x.__class__)")

    def test_nested_format_blocked(self):
        """Nested format strings."""
        with pytest.raises((SecurityError, ValueError, SyntaxError)):
            safe_parse("'{}'.format('{}'.format(__import__))")


class TestNullByteInjection:
    """Test null byte injection prevention."""

    def test_null_in_expression(self):
        """Null byte in middle of expression."""
        with pytest.raises((SecurityError, ValueError)):
            safe_parse("x\x00 + y")

    def test_null_in_function_call(self):
        """Null byte in function name."""
        with pytest.raises((SecurityError, ValueError)):
            safe_parse("sin\x00(x)")

    def test_null_after_import(self):
        """Null byte to terminate string early."""
        with pytest.raises((SecurityError, ValueError)):
            safe_parse("import\x00os")

    def test_multiple_nulls(self):
        """Multiple null bytes."""
        with pytest.raises((SecurityError, ValueError)):
            safe_parse("x\x00\x00\x00y")


class TestEncodingBypass:
    """Test encoding-based bypass attempts."""

    def test_hex_escape_import(self):
        """Hex escapes to hide __import__."""
        with pytest.raises((SecurityError, ValueError, SyntaxError)):
            safe_parse("\\x5f\\x5fimport\\x5f\\x5f('os')")

    def test_octal_escape(self):
        """Octal escapes."""
        with pytest.raises((SecurityError, ValueError, SyntaxError)):
            safe_parse("\\137\\137import\\137\\137('os')")

    def test_unicode_escape(self):
        """Unicode escapes."""
        with pytest.raises((SecurityError, ValueError, SyntaxError)):
            safe_parse("\\u005f\\u005fimport\\u005f\\u005f('os')")

    def test_base64_encoded_payload(self):
        """Base64 encoded malicious payload."""
        # Even if decoded, should be blocked
        with pytest.raises((SecurityError, NameError, ValueError)):
            safe_parse("__import__('base64').b64decode('X19pbXBvcnRfXygnb3MnKQ==')")


class TestLambdaObfuscation:
    """Test lambda-based obfuscation."""

    def test_lambda_import_blocked(self):
        """Lambda wrapping import."""
        with pytest.raises((SecurityError, SyntaxError)):
            safe_parse("(lambda: __import__('os'))()")

    def test_lambda_eval_blocked(self):
        """Lambda wrapping eval."""
        with pytest.raises((SecurityError, SyntaxError)):
            safe_parse("(lambda x: eval(x))('1+1')")

    def test_lambda_getattr_blocked(self):
        """Lambda with getattr."""
        with pytest.raises((SecurityError, SyntaxError)):
            safe_parse("(lambda: getattr(__builtins__, 'eval'))()('1+1')")


class TestConstructorAccess:
    """Test constructor-based exploitation."""

    def test_type_constructor_blocked(self):
        """type() constructor to create malicious classes."""
        with pytest.raises((SecurityError, NameError, TypeError)):
            safe_parse("type('x', (), {'__code__': compile('import os', '', 'exec')})")

    def test_class_via_bases_blocked(self):
        """Class introspection via __bases__."""
        with pytest.raises((SecurityError, AttributeError, KeyError)):
            safe_parse("[].__class__.__base__.__subclasses__()")

    def test_object_subclasses_blocked(self):
        """object.__subclasses__() enumeration."""
        with pytest.raises((SecurityError, AttributeError, NameError)):
            safe_parse("object.__subclasses__()")


class TestChainedExploitation:
    """Test chained exploitation attempts."""

    def test_multi_stage_import(self):
        """Multi-stage import obfuscation."""
        with pytest.raises((SecurityError, NameError, ValueError)):
            safe_parse("getattr(getattr(__builtins__, 'dict'), '__getitem__')('__import__')('os')")

    def test_nested_introspection(self):
        """Nested introspection chain."""
        with pytest.raises((SecurityError, AttributeError, KeyError)):
            safe_parse("().__class__.__base__.__subclasses__()[104].__init__.__globals__['sys']")

    def test_mixed_encoding_chain(self):
        """Mix multiple encoding techniques."""
        with pytest.raises((SecurityError, SyntaxError, ValueError)):
            safe_parse("\\x5f\\x5f\\u0069mport\\x5f\\x5f('os')")


class TestRightToLeftOverride:
    """Test right-to-left override attacks."""

    def test_rtlo_attack(self):
        """Right-to-left override character (U+202E)."""
        # Makes text display in reverse order
        rtlo_attack = "\u202e\u0065\u0078\u0065\u0063"  # Displays as "exec" reversed

        with pytest.raises((SecurityError, ValueError, SyntaxError)):
            safe_parse(rtlo_attack)

    def test_rtlo_with_code(self):
        """RTL override combined with actual code."""
        with pytest.raises((SecurityError, ValueError)):
            safe_parse("x + \u202e exec('code') \u202c + y")


class TestCommentInjection:
    """Test comment-based injection attempts."""

    def test_comment_escape_attempt(self):
        """Attempt to escape via comments."""
        # Note: Python expressions don't support comments in parse mode
        with pytest.raises((SecurityError, SyntaxError)):
            safe_parse("x + 1 # __import__('os')")

    def test_multiline_comment_escape(self):
        """Multiline comment escape attempt."""
        with pytest.raises((SecurityError, SyntaxError)):
            safe_parse("x + 1 ''' __import__('os') '''")


class TestAttributeAccessChains:
    """Test attribute access chain exploits."""

    def test_deep_attribute_chain(self):
        """Deep attribute access to reach builtins."""
        with pytest.raises((SecurityError, AttributeError, NameError)):
            safe_parse("x.__class__.__class__.__class__.__bases__[0]")

    def test_mro_navigation(self):
        """Navigate class hierarchy via MRO."""
        with pytest.raises((SecurityError, AttributeError)):
            safe_parse("x.__class__.__mro__[1].__subclasses__()")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
