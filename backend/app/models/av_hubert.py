import logging
import os
import sys

import torch
import torch.nn.functional as F

from app.models.base import BaseVSRModel

logger = logging.getLogger(__name__)

CHECKPOINT_PATH = "checkpoints/vsr_base_full_model.pt"
MAX_GEN_TOKENS = 500

AVHUBERT_DIR = os.environ.get("AVHUBERT_DIR") or os.path.join(
    os.path.dirname(__file__), "..", "..", "vendor", "av_hubert"
)


class AVHubertModel(BaseVSRModel):
    def __init__(self, device: torch.device):
        self._device = device
        self._model_name = "av-hubert"
        self._model, self._tgt_dict = self._try_load(device)

    @staticmethod
    def _try_load(device):
        model = None
        tgt_dict = None
        try:
            sys.path.insert(0, AVHUBERT_DIR)
            import fairseq  # noqa: F401
            import avhubert  # noqa: F401 — registers custom model architectures

            model = torch.load(CHECKPOINT_PATH, map_location=device, weights_only=False)
            model.eval()
            model.num_updates = float("inf")
            tgt_dict = model.decoder.dictionary
            logger.info("AV-HuBERT VSR model loaded successfully (vocab: %d)", len(tgt_dict))
        except Exception:
            logger.exception("Could not load AV-HuBERT model")
        return model, tgt_dict

    def predict(self, tensor: torch.Tensor) -> torch.Tensor:
        if self._model is None:
            return torch.randn(tensor.shape[0], 1, 500, device=self._device)

        with torch.no_grad():
            t = tensor.to(self._device)

            if t.dim() == 5:
                t = t.permute(0, 2, 1, 3, 4)

            if t.shape[1] == 3:
                t = t.mean(dim=1, keepdim=True)

            encoder_out = self._model.encoder(
                source={"video": t, "audio": None}, padding_mask=None
            )

            eos = self._tgt_dict.eos()
            vocab_size = len(self._tgt_dict)

            bsz = t.shape[0]
            prev_tokens = t.new_full((bsz, 1), fill_value=eos, dtype=torch.long)
            all_logits = []

            for _ in range(MAX_GEN_TOKENS):
                decoder_out = self._model.decoder(
                    prev_output_tokens=prev_tokens, encoder_out=encoder_out
                )
                logits = decoder_out[0]
                all_logits.append(logits[:, -1:, :])
                next_token = logits[:, -1, :].argmax(dim=-1, keepdim=True)
                prev_tokens = torch.cat([prev_tokens, next_token], dim=1)

                if (next_token == eos).all():
                    break

            return torch.cat(all_logits, dim=1)

    def device(self) -> str:
        return str(self._device)

    def model_name(self) -> str:
        return self._model_name
