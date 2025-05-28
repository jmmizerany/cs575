from abc import ABC, abstractmethod
import datetime
import time
import random

# change this to the desired timeout in seconds
RESET_TIMEOUT_SECONDS = 5

class Context:
    _state = None
    def __init__(self, state: 'State') -> None:
        self.setState(state)
    
    def setState(self, state: 'State'):
        self._state = state
        self._state.context = self

class State(ABC):
    @property
    def context(self) -> Context:
        return self._context
    
    @context.setter
    def context(self, context: Context):
        self._context = context

    @abstractmethod
    def failed_call(self):
        pass

    @abstractmethod
    def successful_call(self):
        pass

class ClosedState(State):
    def __str__(self):
        return "CLOSED"
    
    def failed_call(self):
        print("Call failed in CLOSED state, switching to HALF_OPEN")
        self.context.setState(HalfOpenState())
    
    def successful_call(self):
        print("Call succeeded in CLOSED state, remaining CLOSED")
        # Stay in closed state

class OpenState(State):
    def __init__(self):
        self._open_time = datetime.datetime.now()
        
    def __str__(self):
        return "OPEN"
    
    def failed_call(self):
        print("Circuit is OPEN, call not attempted")
    
    def successful_call(self):
        print("Circuit is OPEN, call not attempted")

class HalfOpenState(State):
    def __str__(self):
        return "HALF_OPEN"
    
    def failed_call(self):
        print("Call failed in HALF_OPEN state, switching to OPEN")
        self.context.setState(OpenState())
    
    def successful_call(self):
        print("Call succeeded in HALF_OPEN state, switching to CLOSED")
        self.context.setState(ClosedState())

class CircuitBreaker(State):
    def __init__(self) -> None:
        # Initialize the circuit breaker in a closed state
        self._context = Context(ClosedState())
        self.delay = RESET_TIMEOUT_SECONDS
        self._open_time = None
    
    def failed_call(self):
        current_state = self.context._state
        print(f"Failed call in {current_state} state")
        current_state.failed_call()
    
    def successful_call(self):
        current_state = self.context._state
        print(f"Successful call in {current_state} state")
        current_state.successful_call()

    def handle_open_state(self):
        current_state = self.context._state
        
        if isinstance(current_state, OpenState):
            if self._open_time is None:
                self._open_time = datetime.datetime.now()
                
            diff_time = (datetime.datetime.now() - self._open_time).total_seconds()
            
            if diff_time < self.delay:
                remaining = self.delay - diff_time
                print(f"Circuit is OPEN. Please wait {remaining:.1f} seconds before retrying")
            else:
                print("Timeout elapsed, moving to HALF_OPEN")
                self.context.setState(HalfOpenState())
                self._open_time = None
        
        elif isinstance(current_state, ClosedState):
            # Do nothing, we're in closed state
            pass
        
        elif isinstance(current_state, HalfOpenState):
            # Let the next call determine the state
            pass

if __name__ == "__main__":
    cb = CircuitBreaker()

    try:
        while True:
            # Check if we need to handle timeouts in OPEN state
            cb.handle_open_state()
            
            # mock a random call (using random library)
            call_success = random.random() >= 0.25
            
            if call_success:
                print("Call was successful")
                cb.successful_call()
            else:
                print("Call failed")
                cb.failed_call()
            
            # Sleep a bit to see the output
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting circuit breaker simulation")