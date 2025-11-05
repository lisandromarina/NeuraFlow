import os
from core.node_factory import NodeFactory
from core.logger import Logger
from services.user_credential_service import UserCredentialService
from openai import OpenAI
from openai import APIError, APIConnectionError, APITimeoutError, RateLimitError


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
                
                return {
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

