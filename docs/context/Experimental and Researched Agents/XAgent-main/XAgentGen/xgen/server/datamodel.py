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

from pydantic import BaseModel
from typing import Optional

class FuncReq(BaseModel):
    """The request for function call"""
    messages:Optional[list[dict]]
    arguments:Optional[dict]
    functions:Optional[list[dict]]
    function_call:Optional[dict]
    temperature:Optional[float]
    max_tokens:Optional[int]
    top_p:Optional[float]
    top_k:Optional[int]
    repetition_penalty:Optional[float]
    model:str


class Usage(BaseModel):
    """The record for token consumption"""
    prompt_tokens:int
    completion_tokens:int
    total_tokens:int

class FuncResult(BaseModel):
    """The response for function call"""
    arguments:Optional[dict]
    function_call:Optional[dict]

class Message(BaseModel):
    content: str

class XAgentMessage(BaseModel):
    message:Message
    finish_reason:str
    index:int

class XAgentResponse(BaseModel):
    model:str
    usage:Optional[Usage]
    choices:list[XAgentMessage]
