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

from XAgent.logs import logger
from XAgent.config import CONFIG,get_apiconfig_by_model,get_model_name
import requests
import traceback


def chatcompletion_request(**kwargs):
    # logger.info(f"xagent received {json.dumps(kwargs)}")
    model_name = get_model_name(kwargs.pop('model',CONFIG.default_completion_kwargs['model']))
    logger.debug("chatcompletion: using " + model_name)
    chatcompletion_kwargs = get_apiconfig_by_model(model_name)
    chatcompletion_kwargs.update(kwargs)

    response = requests.post(
        chatcompletion_kwargs.get("api_base","http://127.0.0.1:8000/chat/completions"),
        headers={"accept": "application/json", "Content-Type": "application/json"},
        json={
            "model": model_name,
            "repetition_penalty": chatcompletion_kwargs.get("repetition_penalty", 1.2),
            "temperature": chatcompletion_kwargs.get("temperature", 0.8),
            "top_p":chatcompletion_kwargs.get("top_p", 1.0),
            "frequency_penalty":chatcompletion_kwargs.get("frequency_penalty",0.5),
            "presence_penalty":chatcompletion_kwargs.get("presence_penalty", 0.0),
            "max_tokens":chatcompletion_kwargs.get("max_tokens", 4096),
            "messages": chatcompletion_kwargs.get("messages", []),
            "arguments": chatcompletion_kwargs.get("arguments", {}),
            "functions": chatcompletion_kwargs.get("functions", []),
            "function_call": chatcompletion_kwargs.get("function_call", {}),
        }
    ).json()

    return response
