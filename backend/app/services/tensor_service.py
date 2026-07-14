import numpy as np
import torch

from app.domain.interfaces import TensorService
from app.domain.models import PipelineContext


class TensorServiceImpl(TensorService):
    def create_tensor(self, ctx: PipelineContext) -> PipelineContext:
        ctx.progress = "creating_tensor"

        if not ctx.mouth_frames:
            ctx.errors.append("No mouth frames to create tensor from")
            return ctx

        # Model expects input normalized with mean=0.421, std=0.165 (in [0,1] range)
        frames_np = np.stack(ctx.mouth_frames, axis=0).astype(np.float32)
        frames_np = frames_np / 255.0
        frames_np = (frames_np - 0.421) / 0.165

        tensor = torch.from_numpy(frames_np).permute(0, 3, 1, 2).unsqueeze(0)
        ctx.tensor = tensor

        return ctx
