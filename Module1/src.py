from abc import ABC, abstractmethod

class Context:
    _state = None
    def __init__(self, state: 'State') -> None:
        self.setState(state)
    
    def setState(self, state: 'State'):
        self._state = state
        self._state.context = self
    
    def doSomething(self):
        self._state.doSomething()

class State(ABC):
    @property
    def context(self) -> Context:
        return self._context
    
    @context.setter
    def context(self, context: Context):
        self._context = context
    
    @abstractmethod
    def doSomething(self) -> None:
        pass
class CircuitStates:
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

class CircuitBreaker(State):
    def __init__(self) -> None:
        # Initialize the circuit breaker in a closed state
        self.context.setState(CircuitStates.CLOSED)