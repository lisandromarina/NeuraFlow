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
        factor_a = config.get("factorA", 1)
        factor_b = config.get("factorB", 1)

        result = factor_a * factor_b
        print(f"[MultiplyNode] factorA={factor_a}, factorB={factor_b}, result={result}")
        return result