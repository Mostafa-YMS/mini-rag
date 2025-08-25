import logging

from openai import OpenAI

from ..LLMEnums import OpenAIRolesEnums
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

        self.__generation_model_id = None
        self.__embedding_model_id = None
        self.embedding_size = None

        self.client = OpenAI(api_key=self.api_key)
        self.logger = logging.getLogger(__name__)

    def set_generation_model(self, model_id: str):
        self.__generation_model_id = model_id

    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.__embedding_model_id = model_id
        self.embedding_size = embedding_size

    def __process_text(self, text: str):
        return text[: self.max_input_chars].strip()

    def construct_prompt(self, prompt: str, role: OpenAIRolesEnums):
        return {"role": role, "content": self.__process_text(prompt)}

    def generate_text(
        self,
        prompt: str,
        max_tokens: int = None,
        temperature: float = None,
        chat_history: list = [],
    ):
        if not self.client:
            self.logger.error("OpenAI client not initialized.")
            return None

        if not self.__generation_model_id:
            self.logger.error("Generation model not set.")
            return None

        max_tokens = max_tokens if max_tokens else self.max_output_tokens
        temperature = temperature if temperature else self.temperature
        chat_history.append(
            self.__construct_prompt(prompt=prompt, role=OpenAIRolesEnums.USER)
        )

        response = self.client.chat.completions.create(
            model=self.__generation_model_id,
            messages=chat_history,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        if (
            not response
            or not response.choices
            or len(response.choices) == 0
            or not response.choices[0].message
        ):
            self.logger.error("Failed to generate text.")
            return None

        return response.choices[0].message.content

    def embed_text(self, text: str, document_type: str):
        if not self.client:
            self.logger.error("OpenAI client not initialized.")
            return None
        if not self.__embedding_model_id:
            self.logger.error("Embedding model not set.")
            return None
        response = self.client.embeddings.create(
            input=text, model=self.__embedding_model_id
        )
        if (
            not response
            or not response.data
            or len(response.data) == 0
            or not response.data[0].embedding
        ):
            self.logger.error("Failed to embed text.")
            return None
        return response.data[0].embedding
