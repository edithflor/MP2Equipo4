from dataset_quality.app import root


def test_root_describes_service() -> None:
    response = root()

    assert response["service"] == "dataset-quality"
