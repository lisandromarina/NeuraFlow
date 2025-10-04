# engine/node_factory.py
class NodeFactory:
    executors = {}

    @classmethod
    def register(cls, node_type):
        def decorator(executor_cls):
            cls.executors[node_type] = executor_cls
            return executor_cls
        return decorator

    @classmethod
    def get_executor(cls, node_type):
        executor_cls = cls.executors.get(node_type)
        
        if not executor_cls:
            raise ValueError(f"No executor found for node type '{node_type}'")
        return executor_cls()
