from enum import Enum


class LLMEnumeration(Enum):
    openai = "openai"
    cohere = "cohere"

class OpenAIRolesEnums(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
