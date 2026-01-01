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

import threading
from concurrent.futures import ThreadPoolExecutor
import yagmail
from colorama import Fore

from XAgentServer.application.core.envs import XAgentServerEnv
from XAgentServer.exts.redis_ext import RedisClient

broadcast_lock = threading.Lock()
executor: ThreadPoolExecutor = None
yag: yagmail.SMTP = None

redis = RedisClient()

# 初始化删除所有的key
redis.delete_all_keys()


def init_yag(logger):
    """init yagmail service

    Args:
        logger (_type_): _description_
    """
    global yag
    if XAgentServerEnv.Email.send_email:
        yag = yagmail.SMTP(user=XAgentServerEnv.Email.email_user,
                           password=XAgentServerEnv.Email.email_password,
                           host=XAgentServerEnv.Email.email_host)
        logger.info("init yagmail")


def init_executor(logger):
    """init a thread pool executor

    Args:
        logger (_type_): _description_
    """
    global executor
    logger.typewriter_log(
        title=f"init a thread pool executor, max_workers: {XAgentServerEnv.workers}",
        title_color=Fore.RED)
    executor = ThreadPoolExecutor(max_workers=XAgentServerEnv.workers)
