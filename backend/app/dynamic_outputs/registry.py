class DynamicOutputRegistry:
    """Registry that maps builder names to callables returning output metadata."""

    _builders = {}

    @classmethod
    def register(cls, name, builder):
        if not callable(builder):
            raise ValueError("Dynamic output builder must be callable")
        cls._builders[name] = builder

    @classmethod
    def get_outputs(cls, name, node_config):
        builder = cls._builders.get(name)
        if not builder:
            raise ValueError(f"No dynamic output builder registered as '{name}'")
        return builder(node_config or {})
