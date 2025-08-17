import logging

import cohere

from ..LLMEnum import CohereRolesEnums, DocumentTypeEnums
from ..LLMInterface import LLMInterface


class CohereProvider(LLMInterface):
    def __init__(
        self,
        api_key: str,
        max_input_chars: int = 1000,
        max_output_tokens: int = 1000,
        temperature: float = 0.1,
    ):
        super().__init__()
        self.api_key = api_key
        self.max_input_chars = max_input_chars
        self.max_output_tokens = max_output_tokens
        self.temperature = temperature

        self.__generation_model_id = None
        self.__embedding_model_id = None
        self.__embedding_size = None

        self.client = cohere.Client(api_key=self.api_key)
        self.logger = logging.getLogger(__name__)

    def set_generation_model(self, model_id: str):
        self.__generation_model_id = model_id

    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.__embedding_model_id = model_id
        self.__embedding_size = embedding_size

    def __process_text(self, text: str):
        return text[: self.max_input_chars].strip()

    def __construct_prompt(self, prompt: str, role: CohereRolesEnums):
        return {"role": role, "message": self.__process_text(prompt)}

    def generate_text(
        self,
        prompt: str,
        max_tokens: int = None,
        temperature: float = None,
        chat_history: list = [],
    ):
        if not self.client:
            self.logger.error("Cohere client not initialized.")
            return None

        if not self.__generation_model_id:
            self.logger.error("Generation model not set.")
            return None

        max_tokens = max_tokens if max_tokens else self.max_output_tokens
        temperature = temperature if temperature else self.temperature

        response = self.client.chat(
            model=self.__generation_model_id,
            chat_history=chat_history,
            max_tokens=max_tokens,
            temperature=temperature,
            message=self.__process_text(text=prompt),
        )

        if not response or not response.text:
            self.logger.error("Failed to generate text.")
            return None

        return response.choices[0].message.content

    def embed_text(self, text: str, document_type: str = None):
        if not self.client:
            self.logger.error("Cohere client not initialized.")
            return None

        if not self.__embedding_model_id:
            self.logger.error("Embedding model not set.")
            return None

        input_type = CohereRolesEnums.DOCUMENT
        if document_type == DocumentTypeEnums.QUERY:
            input_type = CohereRolesEnums.QUERY

        response = self.client.embed(
            texts=[self.__process_text(text)],
            input_type=input_type,
            model=self.__embedding_model_id,
            embedding_types=["float"],
        )
        if (
            not response
            or not response.embeddings
            or len(response.embeddings.float) == 0
            or not response.embeddings.float[0]
        ):
            self.logger.error("Failed to embed text.")
            return None
        return response.embeddings.float[0] 
