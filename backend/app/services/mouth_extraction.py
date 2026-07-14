import os

import cv2
import mediapipe as mp
import numpy as np

from app.domain.interfaces import MouthExtractionService
from app.domain.models import PipelineContext

FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
RunningMode = mp.tasks.vision.RunningMode

MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "models",
    "face_landmarker.task",
)

UPPER_LIP_IDS = [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291]
LOWER_LIP_IDS = [146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 409]
MOUTH_INDICES = list(set(UPPER_LIP_IDS + LOWER_LIP_IDS))

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


class MouthExtractionServiceImpl(MouthExtractionService):
    def extract(self, ctx: PipelineContext) -> PipelineContext:
        ctx.progress = "extracting_mouth"

        if not ctx.frames:
            ctx.errors.append("No frames to extract mouth from")
            return ctx

        landmarker = _get_landmarker()
        mouth_size = (88, 88)
        mouth_frames = []

        for frame in ctx.frames:
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
            result = landmarker.detect(mp_image)

            if not result.face_landmarks:
                h, w = frame.shape[:2]
                x_min, x_max = w // 4, 3 * w // 4
                y_min, y_max = h // 3, 2 * h // 3
                crop = frame[y_min:y_max, x_min:x_max]
                if crop.size == 0:
                    crop = frame
                crop_resized = _resize_with_aspect(crop, mouth_size)
                mouth_frames.append(crop_resized)
                continue

            landmarks = result.face_landmarks[0]
            h, w = frame.shape[:2]

            mouth_pts = np.array(
                [
                    (landmarks[i].x * w, landmarks[i].y * h)
                    for i in MOUTH_INDICES
                ]
            )

            x_min = max(0, int(np.min(mouth_pts[:, 0])) - 10)
            x_max = min(w, int(np.max(mouth_pts[:, 0])) + 10)
            y_min = max(0, int(np.min(mouth_pts[:, 1])) - 10)
            y_max = min(h, int(np.max(mouth_pts[:, 1])) + 10)

            crop = frame[y_min:y_max, x_min:x_max]
            if crop.size == 0:
                if mouth_frames:
                    mouth_frames.append(mouth_frames[-1])
                continue

            crop_resized = _resize_with_aspect(crop, mouth_size)
            mouth_frames.append(crop_resized)

        ctx.mouth_frames = mouth_frames
        if not mouth_frames:
            ctx.errors.append("No mouth frames extracted")

        return ctx


def _resize_with_aspect(
    img: np.ndarray, target: tuple[int, int]
) -> np.ndarray:
    h, w = img.shape[:2]
    scale = min(target[0] / w, target[1] / h)
    new_w = int(w * scale)
    new_h = int(h * scale)
    resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

    canvas = np.zeros((target[1], target[0], 3), dtype=np.uint8)
    x_off = (target[0] - new_w) // 2
    y_off = (target[1] - new_h) // 2
    canvas[y_off : y_off + new_h, x_off : x_off + new_w] = resized
    return canvas
