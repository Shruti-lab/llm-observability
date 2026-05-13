import time
import logging
import httpx
from typing import Any, Dict 
from config import settings


logger = logging.getLogger(__name__)


class LLMClient():
    """Client for querying llama.cpp LLM server"""

    def __init__(self):
        self.base_url = settings.llm_url
        self.model = settings.llm_model
        self.timeout = settings.timeout

    async def query(self, prompt: str) -> Dict[str, Any]:
        """
        Query the llama.cpp server with a prompt
        
        Args:
            prompt: The text prompt to send to the LLM
        
        Returns:
            {
                "response": str,
                "tokens": int,
                "success": bool,
                "error": str | None,
                "status_code": int
            }
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # llama.cpp API format
                response = await client.post(
                    f"{self.base_url}/completion",
                    json={
                        "prompt": prompt,
                        "n_predict": 128,  # Max tokens to generate
                        "temperature": 0.7,
                        "top_k": 40,
                        "top_p": 0.9,
                        "stop": ["\n\n"],  # Stop sequences
                        "stream": False
                    }
                )
                response.raise_for_status()

                data = response.json()
                
                # llama.cpp response format
                return {
                    "response": data.get("content", ""),
                    "status_code": response.status_code,
                    "tokens": data.get("tokens_predicted", 0),
                    "success": True,
                    "error": None
                }

        except httpx.TimeoutException:
            logger.error(f"Timeout querying LLM: {prompt[:50]}...")
            return {
                "response": "",
                "status_code": 408,
                "tokens": 0,
                "success": False,
                "error": "timeout"
            }
        
        except httpx.ConnectError as e:
            logger.error(f"Connection error: {e}")
            return {
                "response": "",
                "status_code": 503,
                "tokens": 0,
                "success": False,
                "error": "connection_error"
            }
        
        except httpx.RequestError as e:
            logger.error(f"Request failed: {e}")
            return {
                "response": "",
                "status_code": 500,
                "tokens": 0,
                "success": False,
                "error": "request_error"
            }
        
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e}")
            return {
                "response": "",
                "status_code": e.response.status_code,
                "tokens": 0,
                "success": False,
                "error": f"http_{e.response.status_code}"
            }
        
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {
                "response": "",
                "status_code": 500,
                "tokens": 0,
                "success": False,
                "error": "unknown"
            }

    def evaluate_quality(self, response: str, expected: str) -> float:
        """
        Evaluate response quality (simple string match for now)
        
        Args:
            response: The LLM's response text
            expected: The expected answer substring
        
        Returns:
            1.0 if expected substring found, 0.0 otherwise
        """
        return 1.0 if expected.lower() in response.lower() else 0.0


# Singleton instance
llm_client: LLMClient = LLMClient()

 
