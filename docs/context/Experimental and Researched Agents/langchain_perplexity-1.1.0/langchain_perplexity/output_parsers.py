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

import re
from typing import Any, Generic

from langchain_core.output_parsers import JsonOutputParser, PydanticOutputParser
from langchain_core.outputs import Generation
from langchain_core.utils.pydantic import TBaseModel


def strip_think_tags(text: str) -> str:
    """Removes all <think>...</think> tags and their content from text.

    This function removes all occurrences of think tags, preserving text
    before, between, and after the tags. It also handles markdown code fences.

    Args:
        text: The input text that may contain think tags.

    Returns:
        The text with all `<think>...</think>` blocks removed.
    """
    # Remove all <think>...</think> blocks using regex
    # The pattern matches <think> followed by any content (non-greedy) until </think>
    result = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)

    # Remove markdown code fence markers if present
    result = result.strip()
    if result.startswith("```json"):
        result = result[len("```json") :].strip()
    elif result.startswith("```"):
        result = result[3:].strip()

    if result.endswith("```"):
        result = result[:-3].strip()

    return result


class ReasoningJsonOutputParser(JsonOutputParser):
    """A JSON output parser that strips reasoning tags before parsing.

    This parser removes any content enclosed in <think> tags from the input text
    before delegating to the parent JsonOutputParser for JSON parsing.

    """

    def parse_result(self, result: list[Generation], *, partial: bool = False) -> Any:
        """Parse the result of an LLM call to a JSON object.

        Args:
            result: The result of the LLM call.
            partial: Whether to parse partial JSON objects.
                If `True`, the output will be a JSON object containing
                all the keys that have been returned so far.
                If `False`, the output will be the full JSON object.

        Returns:
            The parsed JSON object.

        Raises:
            OutputParserException: If the output is not valid JSON.
        """
        text = result[0].text
        text = strip_think_tags(text)
        return super().parse_result([Generation(text=text)], partial=partial)


class ReasoningStructuredOutputParser(
    PydanticOutputParser[TBaseModel], Generic[TBaseModel]
):
    """A structured output parser that strips reasoning tags before parsing.

    This parser removes any content enclosed in <think> tags from the input text
    before delegating to the parent PydanticOutputParser for structured parsing.
    """

    def parse_result(self, result: list[Generation], *, partial: bool = False) -> Any:
        """Parse the result of an LLM call to a Pydantic object.

        Args:
            result: The result of the LLM call.
            partial: Whether to parse partial JSON objects.
                If `True`, the output will be a JSON object containing
                all the keys that have been returned so far.
                If `False`, the output will be the full JSON object.
        """
        text = result[0].text
        text = strip_think_tags(text)
        return super().parse_result([Generation(text=text)], partial=partial)
