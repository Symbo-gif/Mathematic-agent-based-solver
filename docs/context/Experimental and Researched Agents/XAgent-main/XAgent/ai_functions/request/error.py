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

class FunctionCallSchemaError(Exception):
    """Exception raised when there is an error in the structure or format of a function call.

    This exception does not accept any arguments or custom messages. It is thrown when there is an issue
    with the schema or structure of a function call, such as passing the wrong data type, too many or too few
    arguments, etc. This error is used to halt execution and signal that the function call needs to be 
    corrected before the program can continue.
    """
    pass
