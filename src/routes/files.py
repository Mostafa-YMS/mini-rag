import logging
import os

import aiofiles
from fastapi import APIRouter, Depends, Request, UploadFile, status
from fastapi.responses import JSONResponse

from controllers import FileController, ProcessController
from models import AssetModel, ChunkModel, ProjectModel
from models.enums import ResponseMessage
from models.schemas import Asset, FileChunk

from .schemas import ProcessRequest

logger = logging.getLogger("uvicorn.error")
files_router = APIRouter(prefix="/files")


@files_router.post("/upload/{project_id}")
async def upload_file(
    request: Request,
    project_id: str,
    file: UploadFile,
    file_controller: FileController = Depends(FileController),
):
    project_model = await ProjectModel.create_instance(request.app.db)
    project = await project_model.get_or_create_project(project_id=project_id)

    is_valid = file_controller.validate_file(file=file, max_size=2)

    if not is_valid:
        return JSONResponse(
            content={
                "message": ResponseMessage.ERROR.value,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    file_path, file_id = file_controller.generate_file_path(
        file_name=file.filename, project_id=project_id
    )

    try:
        async with aiofiles.open(file_path, "wb") as out_file:
            while chunk := await file.read(5012000):
                await out_file.write(chunk)
    except FileNotFoundError:
        logger(f"File not found: {FileNotFoundError}")
        return JSONResponse(
            content={
                "message": ResponseMessage.ERROR.value,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    asset_model = await AssetModel.create_instance(request.app.db)
    asset = await asset_model.create_asset(
        Asset(
            project_id=project.id,
            type="file",
            name=file_id,
            size=os.path.getsize(file_path),
        )
    )

    return JSONResponse(
        content={
            "message": ResponseMessage.SUCCESS.value,
            "file_id": str(asset.id),
        },
        status_code=status.HTTP_200_OK,
    )


@files_router.post("/process/{project_id}")
async def process_file(
    request: Request,
    process_request: ProcessRequest,
    project_id: str,
    process_controller: ProcessController = Depends(ProcessController),
):
    project_model = await ProjectModel.create_instance(request.app.db)
    chunk_model = await ChunkModel.create_instance(request.app.db)
    project = await project_model.get_or_create_project(project_id=project_id)
    asset_model = await AssetModel.create_instance(request.app.db)

    files = []
    if process_request.file_id:
        asset = await asset_model.get_asset(
            name=process_request.file_id, project_id=project.id
        )
        if asset is None:
            return JSONResponse(
                content={
                    "message": "File not found",
                },
                status_code=status.HTTP_404_NOT_FOUND,
            )
        files.append(asset)
    else:
        files = await asset_model.get_project_assets(project_id=project.id, type="file")

    if len(files) == 0:
        return JSONResponse(
            content={
                "message": "File not found",
            },
            status_code=status.HTTP_404_NOT_FOUND,
        )

    if process_request.do_reset:
        await chunk_model.delete_chunks_by_project_id(project_id=project.id)

    count = 0
    for file in files:
        file_id = file.name
        chunks, not_found = process_controller.process_file(
            file_id=file_id,
            chunk_size=process_request.chunk_size,
            overlap=process_request.overlap,
        )
        if not_found:
            continue

        if chunks is None or len(chunks) == 0:
            return JSONResponse(
                content={
                    "message": ResponseMessage.ERROR.value,
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        chunks_records = [
            FileChunk(
                project_id=project.id,
                content=chunk.page_content,
                metadata=chunk.metadata,
                order=i + 1,
                asset_id=file.id,
            )
            for i, chunk in enumerate(chunks)
        ]

        count += await chunk_model.create_bulk_chunks(chunks_records)

    return JSONResponse(
        content={
            "message": ResponseMessage.SUCCESS.value,
            "count": count,
            "files_count": len(files),
        },
        status_code=status.HTTP_200_OK,
    )
