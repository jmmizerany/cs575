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

class ConcreteStateA(State):
    def doSomething(self) -> None:
        print("ConcreteStateA: Doing something in state A")
        self.context.setState(ConcreteStateB())

class ConcreteStateB(State):
    def doSomething(self) -> None:
        print("ConcreteStateB: Doing something in state B")
        self.context.setState(ConcreteStateA())


if __name__ == "__main__":
    # Example usage
    context = Context(ConcreteStateA())
    context.doSomething()  # Should print message from ConcreteStateA and switch to ConcreteStateB
    context.doSomething()  # Should print message from ConcreteStateB and switch back to ConcreteStateA