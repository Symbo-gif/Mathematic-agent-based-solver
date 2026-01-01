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

"""Recorder CRUD"""
import abc
from typing import List

from sqlalchemy.orm import Session

from XAgentServer.database.interface.recorder import RecordDBInterface
from XAgentServer.exts.exception_ext import XAgentDBError
from XAgentServer.models.recorder import XAgentRunningRecord


class RunningRecordCRUD(metaclass=abc.ABCMeta):
    """
    Recorder CRUD
    """

    @classmethod
    def get_record_list(cls, db: Session, record_id: str) -> list[XAgentRunningRecord]:
        """
        get all records
        
        Args:
            db: database session
            record_id: record_id
        """
        try:
            return RecordDBInterface.get_record_list(db=db, record_id=record_id)
        except Exception as e:
            raise XAgentDBError(f"XAgent DB Error [Recorder Module]: {str(e)}") from e

    @classmethod
    def get_record(cls,
                     db: Session,
                     record_id: str | None = None) -> XAgentRunningRecord | None:
        """
        get record by record_id
        
        Args:
            db: database session
            record_id: record_id
        
        Returns:
            record
        
        """
        try:
            return RecordDBInterface.get_record(db=db, record_id=record_id)
        except Exception as e:
            raise XAgentDBError(f"XAgent DB Error [Recorder Module]: {str(e)}") from e

    @classmethod
    def insert_record(cls,
                      db: Session,
                      record: XAgentRunningRecord):
        """
        insert record
        
        Args:
            db: database session
            record: record
        
        """
        try:
            RecordDBInterface.insert_record(db=db, record=record)
        except Exception as e:
            raise XAgentDBError(f"XAgent DB Error [Recorder Module]: {str(e)}") from e

    @classmethod
    def get_record_by_type(cls,
                         db: Session,
                         record_id: str,
                         node_id: str = "",
                         node_type: str = "") -> List[XAgentRunningRecord]:
        """
        get record by id
        
        Args:
            db: database session
            record_id: record_id
        
        Returns:
            record
        
        """
        try:
            return RecordDBInterface.get_record_by_type(db=db,
                                                        record_id=record_id,
                                                        node_id=node_id,
                                                        node_type=node_type)
        except Exception as e:
            raise XAgentDBError(f"XAgent DB Error [Recorder Module]: {str(e)}") from e
