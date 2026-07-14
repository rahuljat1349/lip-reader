import logging

import torch

from app.models.av_hubert import AVHubertModel
from app.models.base import BaseVSRModel

logger = logging.getLogger(__name__)


def detect_device() -> torch.device:
    if torch.cuda.is_available():
        logger.info("Using CUDA device")
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        logger.info("Using Apple MPS device")
        return torch.device("mps")
    logger.info("Using CPU device")
    return torch.device("cpu")


class ModelFactory:
    @staticmethod
    def create(model_name: str = "av-hubert") -> BaseVSRModel:
        device = detect_device()
        logger.info(f"Creating model '{model_name}' on device '{device}'")

        if model_name == "av-hubert":
            return AVHubertModel(device)

        raise ValueError(f"Unknown model: {model_name}")


_model_instance: BaseVSRModel | None = None


def get_model() -> BaseVSRModel:
    global _model_instance
    if _model_instance is None:
        _model_instance = ModelFactory.create()
    return _model_instance
