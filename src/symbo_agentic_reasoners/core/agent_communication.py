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

from .message_bus import message_bus, AgentMessage, MessageType, MessagePriority, MessageDirection
from typing import Dict, Any, Callable, Optional
import time


class AgentProtocol:
    """Base protocol for all agents to ensure consistent communication"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.register_handlers()
        
    def register_handlers(self):
        """Register message handlers for this agent"""
        message_bus.register_handler(self.agent_id, self.handle_message)
        
    def handle_message(self, message: AgentMessage):
        """Process incoming messages"""
        raise NotImplementedError("Subclasses must implement handle_message")
        
    def send_request(self, recipient_id: str, content: Dict[str, Any], 
                    priority: MessagePriority = MessagePriority.NORMAL,
                    timeout: Optional[float] = None) -> str:
        """Send a request message and return the message ID"""
        message = AgentMessage(
            sender_id=self.agent_id,
            recipient_id=recipient_id,
            message_type=MessageType.REQUEST,
            content=content,
            priority=priority,
            timeout=timeout,
            direction=MessageDirection.TO_SPECIALIST
        )
        message_bus.send_message(message)
        return message.message_id
        
    def send_response(self, request_id: str, content: Dict[str, Any]) -> str:
        """Send a response to a request"""
        # In a real implementation, we'd look up the original request
        # to get the sender_id and other details
        message = AgentMessage(
            sender_id=self.agent_id,
            recipient_id="supervisor",  # Would be dynamic in real implementation
            message_type=MessageType.RESPONSE,
            content=content,
            dependencies=[request_id],
            direction=MessageDirection.TO_SUPERVISOR
        )
        message_bus.send_message(message)
        return message.message_id


class SupervisorProtocol(AgentProtocol):
    """Protocol for the supervisor agent"""
    
    def handle_message(self, message: AgentMessage):
        """Perform handle message operation.

        Args:
        message: Description needed

        Returns:
        Result of the operation

        Example:
        >>> result = obj.handle_message(...)
        """
        """Perform handle message operation.

        Args:
        message: Description needed

        Returns:
        Result of the operation

        Example:
        >>> result = obj.handle_message(...)
        """
        if message.message_type == MessageType.REQUEST:
            self.route_request(message)
        elif message.message_type == MessageType.RESPONSE:
            self.process_response(message)
            
    def route_request(self, message: AgentMessage):
        """Route incoming requests to appropriate specialists"""
        # Implementation would analyze message content and route accordingly
        pass
        
    def process_response(self, message: AgentMessage):
        """Perform handle message operation.

        Args:
        message: Description needed

        Returns:
        Result of the operation

        Example:
        >>> result = obj.handle_message(...)
        """
        """Process responses from specialists"""
        # Implementation would aggregate responses and generate final answer
        pass


class SpecialistProtocol(AgentProtocol):
    """Protocol for specialist agents"""
    
    def handle_message(self, message: AgentMessage):
        """Perform handle message operation.

        Args:
        message: Description needed

        Returns:
        Result of the operation

        Example:
        >>> result = obj.handle_message(...)
        """
        if message.message_type == MessageType.REQUEST:
            self.process_request(message)
            
    def process_request(self, message: AgentMessage):
        """Process requests from supervisor"""
        try:
            # Process the request based on content
            result = self.execute_task(message.content)
            
            # Send response back to supervisor
            self.send_response(
                request_id=message.message_id,
                content={"result": result, "status": "success"}
            )
        except Exception as e:
            self.send_response(
                request_id=message.message_id,
                content={"error": str(e), "status": "failed"}
            )
            
    def execute_task(self, content: Dict[str, Any]) -> Any:
        """Execute the specific task - to be implemented by subclasses"""
        raise NotImplementedError
