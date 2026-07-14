from abc import ABC, abstractmethod

import torch


class BaseVSRModel(ABC):
    @abstractmethod
    def predict(self, tensor: torch.Tensor) -> torch.Tensor:
        ...

    @abstractmethod
    def device(self) -> str:
        ...

    @abstractmethod
    def model_name(self) -> str:
        ...
