import cv2
import numpy as np

from fastapi import APIRouter, WebSocket

from app.domain.models import PipelineContext
from app.services.decoder import DecoderServiceImpl
from app.services.face_detection import FaceDetectionServiceImpl
from app.services.inference import InferenceServiceImpl
from app.services.metrics import MetricsService
from app.services.mouth_extraction import MouthExtractionServiceImpl
from app.services.tensor_service import TensorServiceImpl

router = APIRouter()

WINDOW_SIZE = 30
INFERENCE_INTERVAL = 5


@router.websocket("/ws/live")
async def live(websocket: WebSocket):
    await websocket.accept()

    face_detector = FaceDetectionServiceImpl()
    mouth_extractor = MouthExtractionServiceImpl()
    tensor_service = TensorServiceImpl()
    inference_service = InferenceServiceImpl()
    decoder = DecoderServiceImpl()
    metrics = MetricsService()

    frame_buffer: list[np.ndarray] = []
    frame_count = 0
    transcript = ""
    confidence = 0.0

    metrics.start()

    try:
        while True:
            data = await websocket.receive_bytes()

            img = cv2.imdecode(
                np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_COLOR
            )
            if img is None:
                continue

            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_resized = cv2.resize(img_rgb, (224, 224))
            frame_buffer.append(img_resized)
            frame_count += 1

            if len(frame_buffer) > WINDOW_SIZE:
                frame_buffer.pop(0)

            if frame_count % INFERENCE_INTERVAL == 0 and len(frame_buffer) >= INFERENCE_INTERVAL:
                ctx = PipelineContext(
                    frames=list(frame_buffer),
                    progress="detecting_face",
                )

                ctx = face_detector.detect(ctx)
                if ctx.errors:
                    ctx.errors.clear()
                    continue

                ctx = mouth_extractor.extract(ctx)
                if ctx.errors:
                    ctx.errors.clear()
                    continue

                ctx = tensor_service.create_tensor(ctx)
                if ctx.errors:
                    ctx.errors.clear()
                    continue

                ctx = inference_service.infer(ctx)
                if ctx.errors:
                    ctx.errors.clear()
                    continue

                ctx = decoder.decode(ctx)
                if ctx.errors:
                    ctx.errors.clear()
                    continue

                if ctx.transcript:
                    transcript = ctx.transcript
                    confidence = ctx.confidence

                ctx = metrics.record(ctx)

                await websocket.send_json({
                    "transcript": transcript,
                    "confidence": round(confidence, 3),
                    "progress": min(frame_count / 300, 1.0),
                    "final": False,
                })

    except Exception:
        pass
    finally:
        if transcript:
            try:
                await websocket.send_json({
                    "transcript": transcript,
                    "confidence": round(confidence, 3),
                    "progress": 1.0,
                    "final": True,
                })
            except Exception:
                pass
        await websocket.close()
