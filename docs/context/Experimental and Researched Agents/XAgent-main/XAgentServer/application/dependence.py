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

import os

from colorama import Fore
from XAgentServer.application.core.envs import XAgentServerEnv
from XAgentServer.application.global_val import (init_executor, init_yag)
from XAgentServer.loggers.logs import Logger
from XAgentServer.database.connect import SessionLocal


def enable_logger():
    """logger"""
    if not os.path.exists(os.path.join(XAgentServerEnv.base_dir, "logs")):
        os.makedirs(os.path.join(
            XAgentServerEnv.base_dir, "logs"))

    logger = Logger(log_dir=os.path.join(
        XAgentServerEnv.base_dir, "logs"), log_file="app.log", log_name="XAgentServerApp")
    return logger


def enable_dependence(logger):
    """dependence"""
    logger.typewriter_log(
        title="XAgent Service Init Dependence.",
        title_color=Fore.RED)
    init_yag(logger)
    init_executor(logger)
    logger.typewriter_log(
        title="XAgent Service Init Dependence: Complete!",
        title_color=Fore.RED)


def get_db():
    """db"""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
