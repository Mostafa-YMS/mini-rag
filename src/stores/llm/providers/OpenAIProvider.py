from openai import OpenAI

from ..LLMInterface import LLMInterface


class OpenAIProvider(LLMInterface):
    def __init__(
        self,
        api_key: str,
        url: str = None,
        max_input_chars: int = 1000,
        max_output_tokens: int = 1000,
        temperature: float = 0.1,
    ):
        super().__init__()
        self.client = OpenAI
        self.api_key = api_key
        self.url = url
        self.max_input_chars = max_input_chars
        self.max_output_tokens = max_output_tokens
        self.temperature = temperature
        
        self.generation_model_id = None
        self.embedding_model_id = None
        self.embed_size = None
