from typing import Optional

from pydantic import BaseModel


class ProcessRequest(BaseModel):
    file_id: Optional[str] = None
    chunk_size: Optional[int] = 100
    overlap: Optional[int] = 20
    do_reset: Optional[bool] = False
