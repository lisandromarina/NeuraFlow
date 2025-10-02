from core.node_factory import NodeFactory
import requests

@NodeFactory.register("HttpNode")
class HttpExecutor:
    @staticmethod
    def run(config, context):
        """
        Executes an HTTP request.
        Expects:
          - config["url"]: the URL to call
          - config["method"]: GET, POST, PUT, DELETE (default GET)
          - config.get("headers"): optional headers
          - config.get("body"): optional body for POST/PUT
        Returns:
          - dict with status_code and response_json
        """
        url = config.get("url")
        method = config.get("method", "GET").upper()
        headers = config.get("headers", {})
        body = config.get("body", None)

        if not url:
            raise ValueError("HttpNode requires 'url' in config")

        response = requests.request(method, url, headers=headers, json=body)

        # Return a standard structure
        return {
            "status_code": response.status_code,
            "response": response.json() if response.content else None
        }
