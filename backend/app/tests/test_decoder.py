import torch

from app.domain.models import PipelineContext
from app.services.decoder import DecoderServiceImpl


def test_decode_returns_transcript_for_random_logits():
    ctx = PipelineContext()
    ctx.logits = torch.randn(1, 10, 1000)

    service = DecoderServiceImpl()
    result = service.decode(ctx)

    assert isinstance(result.transcript, str)
    assert 0.0 <= result.confidence <= 1.0


def test_decode_with_no_logits_returns_error():
    ctx = PipelineContext()

    service = DecoderServiceImpl()
    result = service.decode(ctx)

    assert any("No logits" in e for e in result.errors)


def test_decode_with_single_prediction():
    ctx = PipelineContext()
    logits = torch.zeros(1, 6, 1000)
    logits[0, 0, 8] = 10.0
    logits[0, 1, 5] = 10.0
    logits[0, 2, 12] = 10.0
    logits[0, 3, 12] = 10.0
    logits[0, 4, 15] = 10.0
    logits[0, 5, 0] = 10.0
    ctx.logits = logits

    service = DecoderServiceImpl()
    result = service.decode(ctx)

    assert len(result.transcript) > 0
