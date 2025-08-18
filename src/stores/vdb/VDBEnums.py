from enum import Enum


class VDBEnums(Enum):
    QDRANT = "QDRANT"


class DistanceMethodEnums(Enum):
    cosine = "cosine"
    dot = "dot"
