import logging

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse

from controllers import NLPController
from models import ChunkModel, ProjectModel

from .schemas import PushRequest, SearchRequest

logger = logging.getLogger("uvicorn.error")

nlp_router = APIRouter(prefix="/nlp", tags=["nlp"])


@nlp_router.post("/index/push/{project_id}")
async def index_project(request: Request, project_id: str, push_request: PushRequest):
    project_model = await ProjectModel.create_instance(db=request.app.db)
    project = await project_model.get_or_create_project(project_id=project_id)

    if not project:
        return JSONResponse(
            content={"message": "Project not found"},
            status_code=status.HTTP_404_NOT_FOUND,
        )

    nlp_controller = NLPController(
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
        vdb_client=request.app.vdb_client,
    )

    chunk_model = await ChunkModel.create_instance(db=request.app.db)

    has_records = True
    page = 1
    count = 0

    while has_records:
        chunks = await chunk_model.get_all_chunks(project_id=project.id, page=page)
        if len(chunks):
            page += 1

        if not chunks or len(chunks) == 0:
            has_records = False
            break

        is_inserted = nlp_controller.index_into_vdb(
            project=project, chunks=chunks, do_reset=push_request.do_reset
        )

        if not is_inserted:
            return JSONResponse(
                content={"message": "Indexing failed"},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        count += len(chunks)

    return JSONResponse(
        content={"message": "Indexing completed", "count": count},
        status_code=status.HTTP_200_OK,
    )


@nlp_router.get("/index/info/{project_id}")
async def get_index_info(request: Request, project_id: str):
    project_model = await ProjectModel.create_instance(db=request.app.db)
    project = await project_model.get_or_create_project(project_id=project_id)

    if not project:
        return JSONResponse(
            content={"message": "Project not found"},
            status_code=status.HTTP_404_NOT_FOUND,
        )

    nlp_controller = NLPController(
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
        vdb_client=request.app.vdb_client,
    )

    nlp_collection = nlp_controller.get_vdb_collection(project=project)

    return JSONResponse(
        content={"message": nlp_collection},
        status_code=status.HTTP_200_OK,
    )


@nlp_router.post("/index/search/{project_id}")
async def search_index(
    request: Request, project_id: str, search_request: SearchRequest
):
    project_model = await ProjectModel.create_instance(db=request.app.db)
    project = await project_model.get_or_create_project(project_id=project_id)

    if not project:
        return JSONResponse(
            content={"message": "Project not found"},
            status_code=status.HTTP_404_NOT_FOUND,
        )

    nlp_controller = NLPController(
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
        vdb_client=request.app.vdb_client,
    )

    results = nlp_controller.search_vdb(
        project=project, text=search_request.text, limit=search_request.limit
    )

    if not results:
        return JSONResponse(
            content={"message": "Search failed"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return JSONResponse(
        content={"message": "Search completed", "results": results},
        status_code=status.HTTP_200_OK,
    )
