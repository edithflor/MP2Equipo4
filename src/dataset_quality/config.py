from typing import Literal

from pydantic import BaseModel, Field, model_validator


class RuleConfig(BaseModel):
    threshold: float = Field(ge=0)
    severity: Literal["warn", "fail"]


class QualityConfig(BaseModel):
    min_images_per_class: RuleConfig


class QualityPolicyConfig(BaseModel):
    """Política versionada para evaluar las salidas de F2/F3."""

    version: int = Field(ge=1)
    min_images_per_class: RuleConfig
    small_objects_percentage: RuleConfig
    class_imbalance_ratio: RuleConfig
    duplicate_pairs: RuleConfig
    invalid_boxes: RuleConfig
    spatial_bias_percentage: RuleConfig


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
