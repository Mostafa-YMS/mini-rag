from typing import List

from models.schemas import FileChunk, Project
from stores.llm.LLMEnums import DocumentTypeEnums
from stores.llm.LLMInterface import LLMInterface
from stores.vdb.VDBInterface import VDBInterface

from .BaseController import BaseController


class NLPController(BaseController):
    def __init__(
        self,
        generation_client: LLMInterface,
        embedding_client: LLMInterface,
        vdb_client: VDBInterface,
    ):
        super().__init__()
        self.generation_client = generation_client
        self.embedding_client = embedding_client
        self.vdb_client = vdb_client

    def create_collection_name(
        self,
        project_id: str,
    ):
        return f"collection_{project_id}".strip()

    def reset_vdb_collection(self, project: Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        return self.vdb_client.delete_collection(collection_name=collection_name)

    def get_vdb_collection(self, project: Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        return self.vdb_client.get_collection(collection_name=collection_name)

    def index_into_vdb(
        self, project: Project, chunks: List[FileChunk], do_reset: bool = False
    ):
        # get collection
        collection_name = self.create_collection_name(project_id=project.project_id)

        # manage items
        texts = [chunk.content for chunk in chunks]
        metadata = [chunk.metadata for chunk in chunks]
        vectors = [
            self.embedding_client.embed_text(
                text=text, document_type=DocumentTypeEnums.DOCUMENT.value
            )
            for text in texts
        ]
        # create collection
        self.vdb_client.create_collection(
            collection_name=collection_name,
            embedding_size=self.embedding_client.embedding_size,
            do_reset=do_reset,
        )

        # index
        self.vdb_client.insert_many(
            collection_name=collection_name,
            texts=texts,
            vectors=vectors,
            metadata=metadata,
        )

        return True
