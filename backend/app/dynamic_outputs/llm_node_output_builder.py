import json
from typing import Dict, List, Any

from .registry import DynamicOutputRegistry


def _load_format_output(config: Dict[str, Any]) -> Any:
    format_output = config.get("format_output")
    if isinstance(format_output, str):
        format_output = format_output.strip()
        if not format_output:
            return None
        try:
            return json.loads(format_output)
        except json.JSONDecodeError:
            return None
    return format_output


def _build_outputs_from_properties(properties: Dict[str, Any]) -> List[Dict[str, Any]]:
    outputs: List[Dict[str, Any]] = []
    for name, schema in properties.items():
        schema_type = schema.get("type", "string") if isinstance(schema, dict) else "string"
        outputs.append({
            "name": name,
            "label": name.replace("_", " ").title(),
            "type": schema_type,
            "schema": schema if isinstance(schema, dict) else None
        })
    return outputs


def llm_node_output_builder(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    dynamic_outputs: List[Dict[str, Any]] = []
    format_output = _load_format_output(config)

    if isinstance(format_output, dict):
        schema_type = format_output.get("type")
        if schema_type == "object" and "properties" in format_output:
            dynamic_outputs.extend(_build_outputs_from_properties(format_output["properties"]))

    default_outputs = [
        {
            "name": "content",
            "label": "Response Content",
            "type": "string"
        },
        {
            "name": "model",
            "label": "Model Used",
            "type": "string"
        },
        {
            "name": "usage",
            "label": "Token Usage",
            "type": "object",
            "schema": {
                "prompt_tokens": "number",
                "completion_tokens": "number",
                "total_tokens": "number"
            }
        },
        {
            "name": "full_response",
            "label": "Full Response",
            "type": "json"
        }
    ]

    return default_outputs + dynamic_outputs


DynamicOutputRegistry.register("LLMNodeOutputBuilder", llm_node_output_builder)
