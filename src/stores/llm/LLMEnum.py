from enum import Enum


class LLMEnumeration(Enum):
    openai = "openai"
    cohere = "cohere"

class OpenAIRolesEnums(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class CohereRolesEnums(Enum):
    SYSTEM = "SYSTEM"
    USER = "USER"
    ASSISTANT = "CHATBOT"
    DOCUMENT = "search_document"
    QUERY = "search_query"


class DocumentTypeEnums(Enum):
    DOCUMENT = "document"
    QUERY = "query"
