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

"""XAgent Running Recorder Type Enum"""


class RecorderTypeEnum:
    """XAgent Running Recorder Type Enum
    """
    QUERY = "query"
    CONFIG = "config"
    LLM_INPUT_PAIR = "llm_input_pair"
    TOOL_SERVER_PAIR = "tool_server_pair"
    NOW_SUBTASK_ID = "now_subtask_id"
    TOOL_CALL = "tool_call"
    PLAN_REFINE = "plan_refine"
    LLM_SERVER_CACHE = "llm_server_cache"
    TOOL_SERVER_CACHE = "tool_server_cache"
    TOOL_CALL_CACHE = "tool_call_cache"
    PLAN_REFINE_CACHE = "plan_refine_cache"
    LLM_INTERFACE_ID = "llm_interface_id"
    TOOL_SERVER_INTERFACE_ID = "toolserver_interface_id"
    TOOL_CALL_ID = "tool_call_id"
    
