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

"""Response body"""
import json
from typing import Union

from pydantic import BaseModel, Json


class ResponseBody(BaseModel):
    """Response body
    """
    data: Union[str, dict, list, Json, None] = None
    success: bool = True
    message: Union[str, None] = None

    def to_dict(self):
        """to dict
        """
        return self.dict()

    def to_json(self):
        """to json
        """
        return self.json()


class WebsocketResponseBody():
    r"""
    WerSocket 返回值对象

    Attributes:
        data: 返回的数据

        status: 状态

        message: 消息

        kwargs: 其他参数, 会被添加到返回值中
    """

    def __init__(self,
                 data: Union[str, dict, list, Json, None],
                 status: str = "success",
                 message: Union[str, None] = None,
                 **kwargs):
        self.data = data
        self.status = status
        self.message = message
        self.extend(kwargs)

    def to_text(self):
        r"""
        返回json格式的字符串
        """

        return json.dumps(self.__dict__, ensure_ascii=False, indent=2)

    def extend(self, extend: dict):
        """extend attributes
        """
        for key, value in extend.items():
            if key not in self.__dict__.keys():
                self.__dict__[key] = value
