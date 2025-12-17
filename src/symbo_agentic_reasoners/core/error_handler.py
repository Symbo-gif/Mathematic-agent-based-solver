class ErrorHandler:
    def __init__(self):
        self.error_history = []
        self.max_retries = 3
        
    def handle_error(self, agent, error, context):
        # Record error with timestamp and context
        error_record = {
            'timestamp': time.time(),
            'agent': agent,
            'error_type': type(error).__name__,
            'error_msg': str(error),
            'context': context,
            'retry_count': 0
        }
        self.error_history.append(error_record)
        
        # Determine appropriate response based on error type
        if self._is_recoverable(error):
            return self._attempt_recovery(error_record)
        else:
            return self._escalate_error(error_record)
        
    def _is_recoverable(self, error):
        # Define which errors are recoverable
        recoverable_errors = [
            'MathDomainError',
            'ConvergenceError',
            'SyntaxError',
            'ValueError'
        ]
        return type(error).__name__ in recoverable_errors
        
    def _attempt_recovery(self, error_record):
        # Implement recovery strategies
        if error_record['retry_count'] < self.max_retries:
            error_record['retry_count'] += 1
            return {
                'action': 'retry',
                'modified_context': self._adjust_context(error_record)
            }
        else:
            return {'action': 'escalate'}
            
    def _adjust_context(self, error_record):
        # Adjust context based on error type
        context = error_record['context'].copy()
        
        if error_record['error_type'] == 'MathDomainError':
            # Adjust domain assumptions
            context['assumptions'] = self._adjust_domain_assumptions(
                context.get('assumptions', {})
            )
            
        elif error_record['error_type'] == 'ConvergenceError':
            # Adjust convergence parameters
            context['parameters'] = self._adjust_convergence_parameters(
                context.get('parameters', {})
            )
            
        return context