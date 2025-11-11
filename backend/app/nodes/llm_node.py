import json
from core.node_factory import NodeFactory
from core.logger import Logger
from services.user_credential_service import UserCredentialService
from openai import OpenAI
from openai import APIError, APIConnectionError, APITimeoutError, RateLimitError


def _load_format_output(config):
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


def _extract_structured_content(content: str):
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # Attempt to locate first JSON object in content
        start = content.find("{")
        end = content.rfind("}")
        if start != -1 and end != -1 and end > start:
            snippet = content[start:end + 1]
            try:
                return json.loads(snippet)
            except json.JSONDecodeError:
                return None
        return None


@NodeFactory.register("LLMNode")
class LLMExecutor:
    """
    A node to interact with OpenAI's API for LLM operations.
    Supports chat completions with configurable model, temperature, and other parameters.
    Uses the official OpenAI Python library for better error handling and features.
    """

    @staticmethod
    def run(config, context):
        # === Extract Services ===
        services = context.get("services", {})
        logger: Logger = services.get("logger")
        user_credential_service: UserCredentialService = services.get("user_credentials")

        user_id = config.get("user_id")
        prompt = config.get("prompt")
        model = config.get("model", "gpt-3.5-turbo")
        temperature = config.get("temperature", 0.7)
        max_tokens = config.get("max_tokens")
        system_prompt = config.get("system_prompt")
        format_output_schema = _load_format_output(config)

        if format_output_schema:
            json_instruction = "You must respond with valid JSON that matches the expected schema."
            if system_prompt:
                system_prompt = f"{system_prompt.strip()}\n\n{json_instruction}"
            else:
                system_prompt = json_instruction

        if not user_id:
            raise ValueError("Missing required config key: 'user_id'")
        if not prompt:
            raise ValueError("Missing required config key: 'prompt'")

        # === Load User Credentials ===
        # Get OpenAI credentials by user_id and service
        decrypted_creds = user_credential_service.get_credentials_by_service(user_id, "openai")
        
        if not decrypted_creds:
            raise ValueError(f"No OpenAI credentials found for user_id {user_id}")

        # Extract the API key
        api_key = decrypted_creds.get("api_key")
        
        if not api_key:
            raise ValueError("OpenAI API key not found in credentials")

        logger.log(f"[LLMNode] Making request to OpenAI with model '{model}'")

        # === Initialize OpenAI Client ===
        client = OpenAI(api_key=api_key)

        # === Build messages array ===
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # === Prepare completion parameters ===
        completion_params = {
            "model": model,
            "messages": messages,
            "temperature": temperature
        }

        if max_tokens:
            completion_params["max_tokens"] = max_tokens

        if isinstance(format_output_schema, dict):
            completion_params["response_format"] = {
                "type": "json_object"
            }

        try:
            # === Make the API request ===
            completion = client.chat.completions.create(**completion_params)
            
            # Extract the response content
            if completion.choices and len(completion.choices) > 0:
                content = completion.choices[0].message.content
                
                logger.log(f"[LLMNode] Successfully received response from OpenAI")
                
                # Build usage info
                usage_info = None
                if completion.usage:
                    usage_info = {
                        "prompt_tokens": completion.usage.prompt_tokens,
                        "completion_tokens": completion.usage.completion_tokens,
                        "total_tokens": completion.usage.total_tokens
                    }
                
                structured_output = None
                if format_output_schema:
                    structured_output = _extract_structured_content(content)

                result = {
                    "content": content,
                    "model": completion.model,
                    "usage": usage_info,
                    "full_response": {
                        "id": completion.id,
                        "object": completion.object,
                        "created": completion.created,
                        "model": completion.model,
                        "choices": [
                            {
                                "index": choice.index,
                                "message": {
                                    "role": choice.message.role,
                                    "content": choice.message.content
                                },
                                "finish_reason": choice.finish_reason
                            }
                            for choice in completion.choices
                        ],
                        "usage": usage_info
                    }
                }
                logger.log(f"[LLMNode] Results: {result}")

                if isinstance(structured_output, dict):
                    result["structured_output"] = structured_output
                    for key, value in structured_output.items():
                        if key not in result:
                            result[key] = value
                elif structured_output is not None:
                    result["structured_output"] = structured_output

                logger.log(f"[LLMNode] Returning object : {result}")
                return result
            else:
                raise ValueError("No choices in OpenAI response")

        except RateLimitError as e:
            logger.log(f"[LLMNode] Rate limit error: {e}")
            raise ValueError(f"OpenAI API rate limit exceeded: {str(e)}")
        except APITimeoutError as e:
            logger.log(f"[LLMNode] Timeout error: {e}")
            raise ValueError(f"OpenAI API request timed out: {str(e)}")
        except APIConnectionError as e:
            logger.log(f"[LLMNode] Connection error: {e}")
            raise ValueError(f"Failed to connect to OpenAI API: {str(e)}")
        except APIError as e:
            logger.log(f"[LLMNode] API error: {e}")
            raise ValueError(f"OpenAI API error: {str(e)}")
        except Exception as e:
            logger.log(f"[LLMNode] Unexpected error: {e}")
            raise ValueError(f"Unexpected error calling OpenAI API: {str(e)}")

