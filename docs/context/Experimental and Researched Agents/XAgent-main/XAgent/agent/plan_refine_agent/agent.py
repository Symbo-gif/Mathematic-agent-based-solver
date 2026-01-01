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

from typing import List
from XAgent.agent.plan_generate_agent import PlanGenerateAgent
from XAgent.utils import RequiredAbilities
from XAgent.message_history import Message

class PlanRefineAgent(PlanGenerateAgent):
    """PlanRefineAgent is a subclass of PlanGenerateAgent and is involved in refining the plan.

    This class utilizes the required ability of plan refinement to parse information 
    and generate a refined plan. It includes placeholders as the desired expressions.

    Attributes:
        abilities: A set of required abilities for the Agent. For PlanRefineAgent, it includes plan refinement.
    """
    abilities = set([RequiredAbilities.plan_refinement])

    def parse(
        self,
        placeholders: dict = {},
        arguments:dict = None,
        functions=None,
        function_call=None,
        stop=None,
        additional_messages: List[Message] = [],
        additional_insert_index: int = -1,
        *args,
        **kwargs
    ):
        """ Parses information in order to refine the existing plan.

        This method fills in placeholders with corresponding expressions, then prompts and 
        additional messages are processed and converged into final messages. Finally, the 
        'generate' method of PlanGenerateAgent class is then invoked on the final messages.

        Args:
            placeholders (dict, optional): Desired expressions to fill in partially completed text snippets.
            arguments (dict, optional): Arguments to the function.
            functions (optional): Functions to be carried out.
            function_call (optional): Functional request from the user.
            stop (optional): Stop parsing at some particular point.
            additional_messages (List[Message], optional): Additional messages to be included in final message.
            additional_insert_index (int, optional): Index in prompt messages where additional messages should be inserted.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            object: A refined plan generated from provided placeholders, arguments, functions, and messages.
        """
        
        prompt_messages = self.fill_in_placeholders(placeholders)
        messages =prompt_messages[:additional_insert_index] + additional_messages + prompt_messages[additional_insert_index:]
        
        return self.generate(
            messages=messages,
            arguments=arguments,
            functions=functions,
            function_call=function_call,
            stop=stop,
            *args,**kwargs
        )
