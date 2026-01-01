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

class StateManager:
    """
    Manages session state for multi-step problem solving.

    Tracks active sessions, state history, and performs automatic cleanup
    of expired sessions.

    Attributes:
        active_sessions: Dictionary mapping session_id to session data
        max_session_age: Maximum session age in seconds (default: 3600 = 1 hour)
    """

    def __init__(self):
        """Initialize state manager with default configuration."""
        self.active_sessions = {}
        self.max_session_age = 3600  # 1 hour

    def create_session(self, problem_id, initial_state):
        """
        Create new problem-solving session.

        Args:
            problem_id: Unique problem identifier
            initial_state: Initial state dictionary

        Returns:
            Unique session identifier
        """
        session_id = f'session_{problem_id}_{int(time.time())}'
        self.active_sessions[session_id] = {
            'state': initial_state,
            'created_at': time.time(),
            'last_active': time.time(),
            'problem_id': problem_id,
            'history': []
        }
        return session_id
        
    def update_state(self, session_id, new_state, action):
        """
        Update session state and record action in history.

        Args:
            session_id: Session identifier
            new_state: New state dictionary
            action: Action that caused state change

        Returns:
            Updated state

        Raises:
            ValueError: If session not found
        """
        if session_id not in self.active_sessions:
            raise ValueError(f'Session {session_id} not found')

        session = self.active_sessions[session_id]
        session['state'] = new_state
        session['last_active'] = time.time()
        session['history'].append({
            'timestamp': time.time(),
            'action': action,
            'state': copy.deepcopy(new_state)
        })
        
        return session['state']
        
    def get_state(self, session_id):
        """
        Retrieve current state for session.

        Args:
            session_id: Session identifier

        Returns:
            Current state dictionary

        Raises:
            ValueError: If session not found
        """
        if session_id not in self.active_sessions:
            raise ValueError(f'Session {session_id} not found')

        self.active_sessions[session_id]['last_active'] = time.time()
        return self.active_sessions[session_id]['state']

    def cleanup_old_sessions(self):
        """
        Remove sessions that exceed max age.

        Automatically removes sessions that haven't been active within
        max_session_age seconds.

        Returns:
            Number of sessions cleaned up
        """
        current_time = time.time()
        old_sessions = [
            sid for sid, session in self.active_sessions.items()
            if current_time - session['last_active'] > self.max_session_age
        ]
        
        for sid in old_sessions:
            del self.active_sessions[sid]
            
        return len(old_sessions)
