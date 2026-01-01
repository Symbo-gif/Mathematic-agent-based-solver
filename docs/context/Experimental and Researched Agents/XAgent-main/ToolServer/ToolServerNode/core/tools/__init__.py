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
This module provides a utility function to import all modules 
in a specified folder.

The "__all__" variable is a list that defines the public interface of a module.
Here it is utilized to dynamically import all modules in the current directory.
"""

from utils import import_all_modules_in_folder

# dynamically import all modules in the current directory 
__all__ = import_all_modules_in_folder(__file__,__name__)
