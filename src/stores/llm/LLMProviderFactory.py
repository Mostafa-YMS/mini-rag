from .LLMEnums import LLMEnumeration
from .providers import *


class LLMProviderFactory:
    def __init__(self, config: dict):
        self.config = config

    def create(self, provider: str):
        if provider == LLMEnumeration.openai.value:
            return OpenAIProvider(
                api_key=self.config["OPENAI_API_KEY"],
                url=self.config["OPENAI_API_URL"],
                max_input_chars=self.config["MAX_INPUT_CHARS"],
                max_output_tokens=self.config["GENERATION_MAX_TOKENS"],
                temperature=self.config["GENERATION_TEMPERATURE"],
            )

        if provider == LLMEnumeration.cohere.value:
            return CohereProvider(
                api_key=self.config["COHERE_API_KEY"],
                max_input_chars=self.config["MAX_INPUT_CHARS"],
                max_output_tokens=self.config["GENERATION_MAX_TOKENS"],
                temperature=self.config["GENERATION_TEMPERATURE"],
            )

        return None
