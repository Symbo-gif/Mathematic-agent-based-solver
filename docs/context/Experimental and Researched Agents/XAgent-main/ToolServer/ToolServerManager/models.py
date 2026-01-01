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

from beanie import Document
from datetime import datetime


class ToolServerNode(Document):
    """
    A class that represents a node in the database. 
    """
    id: str
    short_id: str
    status: str
    health: str
    last_req_time: datetime
    ip: str
    port: int

class NodeChecker(Document):
    manager_id: str
    interval: float
    pid: int
