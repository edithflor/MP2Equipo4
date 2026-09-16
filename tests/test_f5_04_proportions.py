import pytest
from pytest_bdd import given, scenarios, then, when

scenarios("../features/f5-04-split-proportions.feature")


@pytest.fixture
def context():
    return {
        "coco": {
            "categories": [{"id": 1, "name": "A"}],
            "images": [{"id": i} for i in range(1, 101)],
            "annotations": [
                {"image_id": i, "category_id": 1, "bbox": [0, 0, 10, 10]} for i in range(1, 101)
            ],
        },
        "config": {},
        "N": 100,
        "contract": None,
    }


@given("config default")
def step_config_default(context):
    context["config"] = {"train_ratio": 0.70, "val_ratio": 0.15, "test_ratio": 0.15, "seed": 42}


@when("spliteo N imágenes")
def step_spliteo_n(context):
    from dataset_splitting.pipeline import create_split_contract

    context["contract"] = create_split_contract(context["coco"], context["config"])


@then("|train|+|val|+|test| = N")
def step_sum_equals_n(context):
    splits = context["contract"]["splits"]
    total = len(splits["train"]) + len(splits["val"]) + len(splits["test"])
    assert total == context["N"]


@then("las proporciones están cerca de 0.70/0.15/0.15 dentro de redondeo")
def step_proportions_default(context):
    splits = context["contract"]["splits"]
    assert len(splits["train"]) == 70
    assert len(splits["val"]) == 15
    assert len(splits["test"]) == 15


@given("train=0.80 val=0.10 test=0.10")
def step_config_custom(context):
    context["config"] = {"train_ratio": 0.80, "val_ratio": 0.10, "test_ratio": 0.10, "seed": 42}


@then("los tamaños cambian acorde")
def step_custom_sizes(context):
    splits = context["contract"]["splits"]
    assert len(splits["train"]) == 80
    assert len(splits["val"]) == 10
    assert len(splits["test"]) == 10


@then("no toqué el algoritmo, solo config")
def step_algorithm_untouched(context):
    assert context["contract"]["metadata"]["train_ratio"] == 0.80


@given("train+val+test != 1")
def step_invalid_ratios(context):
    context["config"] = {"train_ratio": 0.80, "val_ratio": 0.50, "test_ratio": 0.10}


@then("Pydantic/ingesta de config falla (F2-03)")
def step_fails_validation(context):
    from dataset_splitting.pipeline import create_split_contract

    with pytest.raises(ValueError):
        create_split_contract(context["coco"], context["config"])
