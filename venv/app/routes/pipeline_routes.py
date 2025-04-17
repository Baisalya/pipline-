from fastapi import APIRouter, HTTPException, Form
from ..services.pipeline_service import (
    create_pipeline, get_all_pipelines,
    get_pipeline_by_id, delete_pipeline
)

router = APIRouter()

@router.post("/pipelines")
async def create_pipeline_route(
    pipeline_name: str = Form(...),
    status: str = Form(...),
    canvas_name: str = Form(...)
):
    try:
        return create_pipeline(pipeline_name, status, canvas_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pipelines")
def get_pipelines_route():
    try:
        return get_all_pipelines()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pipelines/{pipeline_id}")
def get_pipeline_route(pipeline_id: int):
    pipeline = get_pipeline_by_id(pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return pipeline

@router.delete("/pipelines/{pipeline_id}")
def delete_pipeline_route(pipeline_id: int):
    result = delete_pipeline(pipeline_id)
    if not result:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return result
