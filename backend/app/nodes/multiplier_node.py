from core.node_factory import NodeFactory


@NodeFactory.register("MultiplyNode")
class MultiplyExecutor:
    @staticmethod
    def run(config, context):
        """
        This node multiplies the parent_result by a config value.
        Expects:
          - context["parent_result"] (direct parent output)
          - config["multiplier"]
        """

        parent_output = context.get("parent_result", 1)

        multiplier = config.get("factorB", 1)
        result = parent_output * multiplier

        print(f"[MultiplyNode] Parent Result: {parent_output}, Multiplier: {multiplier}, Result: {result}")
        return result
