import pytest
from pytest_bdd import given, scenarios, then, when

scenarios("../features/f5-02-seed-reproducible.feature")


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
        "seed": 42,
        "splits_a": None,
        "splits_b": None,
        "splits_diff": None,
    }


@given("seed = 42")
def step_seed_42(context):
    context["seed"] = 42


@when("corro el split dos veces")
def step_run_twice(context):
    from dataset_splitting.stratified import generate_stratified_splits

    context["splits_a"] = generate_stratified_splits(context["coco"], seed=context["seed"])
    context["splits_b"] = generate_stratified_splits(context["coco"], seed=context["seed"])


@then("train_a == train_b")
def step_train_eq(context):
    assert set(context["splits_a"]["train"]) == set(context["splits_b"]["train"])


@then("val_a == val_b")
def step_val_eq(context):
    assert set(context["splits_a"]["val"]) == set(context["splits_b"]["val"])


@then("test_a == test_b")
def step_test_eq(context):
    assert set(context["splits_a"]["test"]) == set(context["splits_b"]["test"])


@then("un diff de los JSON/archivos está vacío")
def step_diff_empty(context):
    diff = set(context["splits_a"]["train"]) ^ set(context["splits_b"]["train"])
    assert len(diff) == 0


@when("corro con seed distinto")
def step_run_diff_seed(context):
    from dataset_splitting.stratified import generate_stratified_splits

    context["splits_a"] = generate_stratified_splits(context["coco"], seed=42)
    context["splits_diff"] = generate_stratified_splits(context["coco"], seed=99)


@then("al menos un split difiere")
def step_splits_differ(context):
    train_a = set(context["splits_a"]["train"])
    train_diff = set(context["splits_diff"]["train"])
    assert train_a != train_diff
