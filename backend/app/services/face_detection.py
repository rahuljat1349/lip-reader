import logging
import os

import mediapipe as mp
import numpy as np

from app.domain.interfaces import FaceDetectionService

logger = logging.getLogger(__name__)
from app.domain.models import FaceTrack, PipelineContext

FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
FaceLandmarkerResult = mp.tasks.vision.FaceLandmarkerResult
RunningMode = mp.tasks.vision.RunningMode

MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "models",
    "face_landmarker.task",
)

_landmarker_instance = None


def _get_landmarker():
    global _landmarker_instance
    if _landmarker_instance is None:
        options = FaceLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=MODEL_PATH),
            running_mode=RunningMode.IMAGE,
            num_faces=1,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False,
        )
        _landmarker_instance = FaceLandmarker.create_from_options(options)
    return _landmarker_instance


class FaceDetectionServiceImpl(FaceDetectionService):
    def detect(self, ctx: PipelineContext) -> PipelineContext:
        ctx.progress = "detecting_face"

        if not ctx.frames:
            ctx.errors.append("No frames to detect face in")
            return ctx

        landmarker = _get_landmarker()
        tracks = []

        for frame in ctx.frames:
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
            result = landmarker.detect(mp_image)

            if result.face_landmarks:
                landmarks = result.face_landmarks[0]
                h, w = frame.shape[:2]
                xs = [lm.x * w for lm in landmarks]
                ys = [lm.y * h for lm in landmarks]
                x_min = int(max(0, min(xs)))
                x_max = int(min(w, max(xs)))
                y_min = int(max(0, min(ys)))
                y_max = int(min(h, max(ys)))
                bbox = (x_min, y_min, x_max, y_max)

                if tracks:
                    tracks[0].bboxes.append(bbox)
                else:
                    tracks.append(
                        FaceTrack(track_id=0, bboxes=[bbox], confidence=1.0)
                    )
            elif tracks:
                tracks[0].bboxes.append(tracks[0].bboxes[-1])

        if not tracks:
            logger.warning("No face detected — using full frame as mouth region")
            h, w = ctx.frames[0].shape[:2]
            margin = int(min(h, w) * 0.1)
            dummy_bbox = (margin, margin, w - margin, h - margin)
            tracks.append(
                FaceTrack(track_id=0, bboxes=[dummy_bbox] * len(ctx.frames), confidence=0.0)
            )

        ctx.tracks = tracks
        return ctx
