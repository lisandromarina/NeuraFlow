from abc import ABC, abstractmethod

class NodeExecutor(ABC):
    def __init__(self, node, context):
        self.node = node
        self.context = context

    @abstractmethod
    def execute(self) -> dict:
        pass
