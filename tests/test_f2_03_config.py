import pytest
from pydantic import ValidationError

from dataset_quality.config import QualityConfig, SplitsConfig


def test_quality_yaml_valid() -> None:
    data = {"min_images_per_class": {"threshold": 300, "severity": "fail"}}
    config = QualityConfig(**data)
    assert config.min_images_per_class.threshold == 300
    assert config.min_images_per_class.severity == "fail"


def test_quality_yaml_malformed() -> None:

    data = {"min_images_per_class": {"threshold": "not_a_number"}}
    with pytest.raises(ValidationError) as exc:
        QualityConfig(**data)

    error_msg = str(exc.value)
    assert "severity" in error_msg
    assert "threshold" in error_msg


def test_splits_valid() -> None:
    config = SplitsConfig(seed=42, train=0.70, val=0.15, test=0.15, tolerance=0.05)
    assert config.train == 0.70


def test_splits_sum_rejected() -> None:
    with pytest.raises(ValidationError) as exc:
        SplitsConfig(seed=42, train=0.70, val=0.20, test=0.20, tolerance=0.05)

    assert "sumar 1.0" in str(exc.value).lower()
