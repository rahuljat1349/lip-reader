from fastapi import APIRouter, HTTPException, UploadFile

from app.domain.models import PipelineContext, PipelineMetrics
from app.domain.schemas import LipReadResponse
from app.graph.workflow import build_graph
from app.services.file_storage import cleanup_job_dir, create_job_dir, save_upload

router = APIRouter()


@router.get("/health")
async def health():
    return {"status": "ok", "app": "LipReader"}


@router.post("/api/v1/lipread", response_model=LipReadResponse)
async def lipread(file: UploadFile):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    job_id, job_dir = create_job_dir()

    try:
        content = await file.read()
        video_path = save_upload(content, job_dir, file.filename)

        ctx = PipelineContext(
            video_path=video_path,
            job_id=job_id,
            progress="uploaded",
        )

        graph = build_graph()
        state = graph.invoke(ctx)

        errors = state.get("errors", [])
        if errors:
            raise HTTPException(
                status_code=400, detail="; ".join(errors)
            )

        metrics = state.get("metrics") or PipelineMetrics()
        return LipReadResponse(
            transcript=state.get("transcript", ""),
            confidence=state.get("confidence", 0.0),
            metrics={
                "device": metrics.device,
                "processingTime": metrics.processing_time,
                "inferenceTime": metrics.inference_time,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        cleanup_job_dir(job_dir)
