from abc import ABC, abstractmethod
import datetime
import time
import random
import logging

# change this to the desired timeout in seconds
RESET_TIMEOUT_SECONDS = 5

# setting log level
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s: %(message)s')

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
        logging.info("Call failed in CLOSED state, switching to HALF_OPEN")
        self.context.setState(HalfOpenState())
    
    def successful_call(self):
        logging.info("Call succeeded in CLOSED state, remaining CLOSED")

class OpenState(State):
    def __init__(self):
        self._open_time = datetime.datetime.now()
        
    def __str__(self):
        return "OPEN"
    
    def failed_call(self):
        logging.info("Circuit is OPEN, call not attempted")
    
    def successful_call(self):
        logging.info("Circuit is OPEN, call not attempted")

class HalfOpenState(State):
    def __str__(self):
        return "HALF_OPEN"
    
    def failed_call(self):
        logging.info("Call failed in HALF_OPEN state, switching to OPEN")
        self.context.setState(OpenState())
    
    def successful_call(self):
        logging.info("Call succeeded in HALF_OPEN state, switching to CLOSED")
        self.context.setState(ClosedState())

class CircuitBreaker(State):
    def __init__(self) -> None:
        # Initialize the circuit breaker in a closed state
        self._context = Context(ClosedState())
        self.delay = RESET_TIMEOUT_SECONDS
        self._open_time = None
    
    def failed_call(self):
        current_state = self.context._state
        logging.info(f"Failed call in {current_state} state")
        current_state.failed_call()
    
    def successful_call(self):
        current_state = self.context._state
        logging.info(f"Successful call in {current_state} state")
        current_state.successful_call()

    def handle_open_state(self):
        current_state = self.context._state
        
        if isinstance(current_state, OpenState):
            if self._open_time is None:
                self._open_time = datetime.datetime.now()
                
            diff_time = (datetime.datetime.now() - self._open_time).total_seconds()
            
            if diff_time < self.delay:
                remaining = self.delay - diff_time
                logging.info(f"Circuit is OPEN. Please wait {remaining:.1f} seconds before retrying")
            else:
                logging.info("Timeout elapsed, moving to HALF_OPEN")
                self.context.setState(HalfOpenState())
                self._open_time = None
        
        elif isinstance(current_state, ClosedState):
            pass
        
        elif isinstance(current_state, HalfOpenState):
            pass

if __name__ == "__main__":
    cb = CircuitBreaker()

    try:
        while True:
            cb.handle_open_state()
            
            # mock a random call (using random library, I chose anything below 0.25 as a failure)
            call_success = random.random() >= 0.25
            
            if call_success:
                logging.info("Call was successful")
                cb.successful_call()
            else:
                logging.info("Call failed")
                cb.failed_call()
            
            # sleeping to make output easier to read
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("\nExiting circuit breaker simulation")