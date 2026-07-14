import logging
import os

import sentencepiece as spm
import torch
import torch.nn.functional as F

from app.domain.interfaces import DecoderService
from app.domain.models import PipelineContext

logger = logging.getLogger(__name__)

BPE_MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "checkpoints",
    "sentencepiece.bpe.model",
)

_sp_model = None


def _get_sp():
    global _sp_model
    if _sp_model is None:
        _sp_model = spm.SentencePieceProcessor()
        _sp_model.Load(BPE_MODEL_PATH)
        logger.info("BPE model loaded (vocab: %d)", _sp_model.GetPieceSize())
    return _sp_model


class DecoderServiceImpl(DecoderService):
    def decode(self, ctx: PipelineContext) -> PipelineContext:
        ctx.progress = "decoding"

        if ctx.logits is None:
            ctx.errors.append("No logits to decode")
            return ctx

        logits = ctx.logits
        if isinstance(logits, torch.Tensor):
            if logits.dim() == 3:
                logits = logits[0]

            probs = F.softmax(logits.float(), dim=-1)
            max_probs, predictions = torch.max(probs, dim=-1)

            confidence = max_probs.mean().item()
            prediction_text = _decode_seq2seq(predictions.tolist())

            ctx.transcript = prediction_text
            ctx.confidence = confidence
        else:
            ctx.errors.append("Unexpected logits format")

        return ctx


def _decode_seq2seq(predictions: list[int]) -> str:
    sp = _get_sp()
    eos_id = sp.eos_id()
    ids = [p for p in predictions if p != eos_id]
    return sp.DecodeIds(ids)
