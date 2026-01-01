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

import abc
import json
from typing import Union


class InteractionParameter(metaclass=abc.ABCMeta):
    """
    交互参数
    """

    def __init__(self,
                    interaction_id: str,
                    parameter_id: str,
                    args: Union[str, dict, None] = None
                    ):
        self.interaction_id = interaction_id
        self.args = args
        self.parameter_id = parameter_id

    def to_dict(self):
        return {
            "interaction_id": self.interaction_id,
            "parameter_id": self.parameter_id,
            "args": self.args,
        }

    def to_json(self):
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

    @classmethod
    def from_json(cls, json_data):
        return cls(**json_data)
    
    @classmethod
    def from_db(cls, interaction):
        return cls(interaction.interaction_id,
                    interaction.parameter_id,
                    interaction.args
                    )
