from abc import ABC, abstractmethod

class BaseNodeHandler(ABC):
    @abstractmethod
    def handle(self, node: dict, workflow_id: int):
        pass

    @abstractmethod
    def cleanup(self, node: dict, workflow_id: int):
        pass