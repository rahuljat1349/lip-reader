import time

import torch

from app.domain.interfaces import InferenceService
from app.domain.models import PipelineContext
from app.models.factory import get_model


class InferenceServiceImpl(InferenceService):
    def infer(self, ctx: PipelineContext) -> PipelineContext:
        ctx.progress = "running_model"

        if ctx.tensor is None:
            ctx.errors.append("No tensor to run inference on")
            return ctx

        model = get_model()
        ctx.metrics.device = model.device()

        start = time.perf_counter()

        try:
            with torch.no_grad():
                logits = model.predict(ctx.tensor)
            ctx.logits = logits
        except Exception as e:
            ctx.errors.append(f"Inference failed: {e}")
            return ctx

        ctx.metrics.inference_time = time.perf_counter() - start
        return ctx
