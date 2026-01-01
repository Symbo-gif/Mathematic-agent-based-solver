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

"""XAgent Running Recorder"""
import abc

from XAgentServer.database.models import RunningRecord


class XAgentRunningRecord(metaclass=abc.ABCMeta):
    """XAgent Running Recorder"""
    def __init__(self,
                 record_id: str,
                 current: str,
                 node_id: str,
                 node_type: str,
                 data: dict,
                 create_time: str,
                 update_time: str,
                 is_deleted: bool,
                 ):
        self.record_id = record_id
        self.current = current
        self.node_id = node_id
        self.node_type = node_type
        self.data = data
        self.create_time = create_time
        self.update_time = update_time
        self.is_deleted = is_deleted

    def to_dict(self):
        """XAgent Running Recorder to dict"""
        return {
            "record_id": self.record_id,
            "current": self.current,
            "node_id": self.node_id,
            "node_type": self.node_type,
            "data": self.data,
            "create_time": self.create_time,
            "update_time": self.update_time,
            "is_deleted": self.is_deleted,
        }

    @classmethod
    def from_db(cls, db: RunningRecord):
        """From db"""
        return cls(
            record_id=db.record_id,
            current=db.current,
            node_id=db.node_id,
            node_type=db.node_type,
            data=db.data,
            create_time=db.create_time,
            update_time=db.update_time,
            is_deleted=db.is_deleted,
        )

    @classmethod
    def from_dict(cls, data: dict):
        """dict to XAgent Running Recorder"""
        return cls(
            record_id=data["record_id"],
            current=data["current"],
            node_id=data["node_id"],
            node_type=data["node_type"],
            data=data["data"],
            create_time=data["create_time"],
            update_time=data["update_time"],
            is_deleted=data["is_deleted"],
        )
