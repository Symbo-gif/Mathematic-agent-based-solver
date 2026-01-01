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

"""Start server"""
import os
import uvicorn

from XAgentServer.application.core.envs import XAgentServerEnv

if __name__ == "__main__":
    os.system("systemctl start nginx")
    uvicorn.run(app="XAgentServer.application.main:app",
                host=XAgentServerEnv.host,
                port=XAgentServerEnv.port,
                reload=XAgentServerEnv.reload,
                workers=XAgentServerEnv.workers)
