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
import importlib
def import_all_modules_in_folder(file,name):
    current_dir = os.path.dirname(file)
    all_modules = []
    for item in os.listdir(current_dir):
        item_path = os.path.join(current_dir, item)
        if os.path.isfile(item_path) and item != '__init__.py' and item.endswith('.py'):
            module_name = item[:-3]
        elif os.path.isdir(item_path) and item != '__pycache__' and os.path.exists(os.path.join(item_path, '__init__.py')) and os.path.isfile(os.path.join(item_path, '__init__.py')):
            module_name = item
        else:
            continue

        full_module_path = f"{name}.{module_name}"
        # print(module_name,full_module_path)
        imported_module = importlib.import_module(full_module_path)
        globals()[module_name] = imported_module
        all_modules.append(imported_module)
    return all_modules
