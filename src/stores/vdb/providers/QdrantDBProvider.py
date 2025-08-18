import logging
from typing import List

from qdrant_client import QdrantClient, models

from ..VDBEnums import DistanceMethodEnums
from ..VDBInterface import VDBInterface


class QdrantDBProvider(VDBInterface):
    def __init__(self, db_path: str, distance_method: str):
        self.client = None
        self.db_path = db_path

        self.logger = logging.getLogger(__name__)

        switcher = {
            DistanceMethodEnums.cosine.value: models.Distance.COSINE,
            DistanceMethodEnums.dot.value: models.Distance.DOT,
        }
        self.distance_method = switcher.get(distance_method, None)

    def connect(self):
        self.client = QdrantClient(path=self.db_path)

    def disconnect(self):
        self.client.close()
        self.client = None

    def is_collection_exists(self, collection_name: str) -> bool:
        return self.client.collection_exists(collection_name)

    def list_collections(self) -> List:
        return self.client.get_collections()

    def get_collection(self, collection_name: str) -> dict:
        return self.client.get_collection(collection_name)

    def delete_collection(self, collection_name: str):
        if self.is_collection_exists(collection_name):
            return self.client.delete_collection(collection_name)

    def create_collection(
        self, collection_name: str, embedding_size: int, do_reset: bool = False
    ):
        if do_reset:
            self.delete_collection(collection_name)

        if not self.is_collection_exists(collection_name):
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=embedding_size, distance=self.distance_method
                ),
            )
            return True
        return False

    def insert_one(
        self,
        collection_name: str,
        text: str,
        vector: list,
        metadata: dict = None,
        record_id: str = None,
    ):
        if not self.is_collection_exists(collection_name):
            self.logger.error("Collection does not exist.")
            return False

        try:
            self.client.upload_records(
                collection_name=collection_name,
                records=[
                    models.Record(
                        vector=vector,
                        payload={"metadata": metadata, "text": text},
                    )
                ],
            )
            return True
        except Exception as e:
            self.logger.error(f"Error inserting records: {e}")
            return False

    def insert_many(
        self,
        collection_name: str,
        texts: list,
        vectors: list,
        metadata: list = None,
        record_ids: list = None,
        batch_size: int = 50,
    ):
        if not self.is_collection_exists(collection_name):
            self.logger.error("Collection does not exist.")
            return False

        if metadata is None:
            metadata = [None] * len(texts)

        if record_ids is None:
            record_ids = [None] * len(texts)

        for i in range(0, len(texts), batch_size):
            batch_end = i + batch_size
            batch_texts = texts[i:batch_end]
            batch_vectors = vectors[i:batch_end]
            batch_metadata = metadata[i:batch_end]

            batch_records = [
                models.Record(
                    vector=batch_vectors[x],
                    payload={"metadata": batch_metadata[x], "text": batch_texts[x]},
                )
                for x in range(len(batch_texts))
            ]

            try:
                self.client.upload_records(
                    collection_name=collection_name, records=batch_records
                )
            except Exception as e:
                self.logger.error(f"Error inserting records: {e}")
                return False

        return True

    def search_by_vector(
        self,
        collection_name: str,
        vector: list,
        limit: int = 5,
    ):
        return self.client.search(
            collection_name=collection_name,
            query_vector=vector,
            limit=limit,
        )
