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
import shutil
import yaml
import logging
from typing import Dict, Any, Union
import uuid

class ManagerConfig:
    """
    This class manages configuration settings for the application.
    Configuration settings are initially loaded from a yaml file. 
    However, if an environment variable exists with the same name as a configuration setting, 
    the value from the environment variable will be used instead.

    Attributes:
        cfg: A dictionary containing all configuration settings.
    """

    def __init__(self, config_file_path="./assets/config/manager.yml"):
        """
        Initializes a new instance of the ManagerConfig class.

        Args:
            config_file_path (str, optional): The path to a yaml file containing configuration settings. 
            Defaults to "./assets/config.yml".
        """
        self.cfg:Dict = yaml.load(open(config_file_path,"r",encoding="utf-8").read(), Loader=yaml.FullLoader)
        for k in os.environ.keys():
            if k in self.cfg:
                self.cfg[k] = os.environ[k]  # overwrite the config with environment variables

    def __getitem__(self, key):
        """
        Returns the value of a configuration setting.

        Args:
            key (str): The name of the configuration setting.

        Returns:
            The value of the configuration setting. 
        """
        return self.cfg[key]

    def dict(self) -> Dict[str, Any]:
        """
        Returns all configuration settings.

        Returns:
            A dictionary containing all configuration settings.
        """
        return self.cfg

    def update(self, new_config: Dict) -> None:
        """
        Updates configuration settings with the values from another dictionary.

        Args:
            new_config (Dict): A dictionary containing the configuration settings to be updated.

        Returns:
            None
        """
        self.cfg.update(new_config)

CONFIG = ManagerConfig()
logger = logging.getLogger(CONFIG['logger'])
logger.setLevel(CONFIG['logger_level'])
MANAGER_ID = uuid.uuid4().hex
