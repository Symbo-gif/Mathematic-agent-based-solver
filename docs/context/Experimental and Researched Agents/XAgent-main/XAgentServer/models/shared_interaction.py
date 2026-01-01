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
Shared interaction base class
"""

import abc
import json


class SharedInteractionBase(metaclass=abc.ABCMeta):
    def __init__(self,
                interaction_id: str,
                user_name: str,
                create_time: str,
                update_time: str,
                description: str,
                agent: str = "",
                mode: str = "",
                is_deleted: bool = False,
                star: int = 0,
                is_audit: bool = False
                ):
        self.interaction_id = interaction_id
        self.user_name = user_name
        self.create_time = create_time
        self.update_time = update_time
        self.description = description
        self.agent = agent
        self.mode = mode
        self.is_deleted = is_deleted
        self.star = star
        self.is_audit = is_audit

    def to_dict(self, include=None, exclude=None):
        data = {
            "interaction_id": self.interaction_id,
            "user_name": self.user_name,
            "create_time": self.create_time,
            "update_time": self.update_time,
            "description": self.description,
            "agent": self.agent,
            "mode": self.mode,
            "is_deleted": self.is_deleted,
            "star": self.star,
            "is_audit": self.is_audit
        }
        if include:
            data = {k: v for k, v in data.items() if k in include}
        if exclude:
            data = {k: v for k, v in data.items() if k not in exclude}
        return data
        
    
    def to_json(self):
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)
    
    @classmethod
    def from_db(cls, interaction):
        return cls(interaction.interaction_id,
                   interaction.user_name,
                   interaction.create_time,
                   interaction.update_time,
                   interaction.description,
                   interaction.agent,
                   interaction.mode,
                   interaction.is_deleted,
                   interaction.star,
                   interaction.is_audit
                   )
        
        
