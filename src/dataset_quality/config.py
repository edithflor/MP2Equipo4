from typing import Literal

from pydantic import BaseModel, model_validator


class RuleConfig(BaseModel):
    threshold: float
    severity: Literal["warn", "fail"]


class QualityConfig(BaseModel):
    min_images_per_class: RuleConfig


class SplitsConfig(BaseModel):
    seed: int
    train: float
    val: float
    test: float
    tolerance: float

    @model_validator(mode="after")
    def check_proportions_sum(self) -> "SplitsConfig":
        total = self.train + self.val + self.test
        if abs(total - 1.0) > 1e-6:
            raise ValueError(
                f"Las proporciones train, val y test deben sumar 1.0 (actual: {total})"
            )
        return self
