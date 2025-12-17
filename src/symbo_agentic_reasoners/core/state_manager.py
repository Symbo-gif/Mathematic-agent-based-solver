class StateManager:
    def __init__(self):
        self.active_sessions = {}
        self.max_session_age = 3600  # 1 hour
        
    def create_session(self, problem_id, initial_state):
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
        if session_id not in self.active_sessions:
            raise ValueError(f'Session {session_id} not found')
            
        self.active_sessions[session_id]['last_active'] = time.time()
        return self.active_sessions[session_id]['state']
        
    def cleanup_old_sessions(self):
        current_time = time.time()
        old_sessions = [
            sid for sid, session in self.active_sessions.items()
            if current_time - session['last_active'] > self.max_session_age
        ]
        
        for sid in old_sessions:
            del self.active_sessions[sid]
            
        return len(old_sessions)