import pytest
from pytest_bdd import given, scenarios, then, when

scenarios("../features/f5-03-no-leakage.feature")


@pytest.fixture
def context():
    return {
        "splits": {"train": [1, 2], "val": [3], "test": [4]},
        "all_images": [1, 2, 3, 4],
        "phash_pairs": [{"image1": 1, "image2": 2, "distance": 0}],
        "bad_splits": {"train": [1], "val": [2, 3], "test": [4]},
        "result": None,
    }


@when("genero los splits")
def step_genero_splits(context):
    from dataset_splitting.leakage import analyze_leakage

    context["result"] = analyze_leakage(
        context["splits"], context["all_images"], context["phash_pairs"]
    )


@then("train ∩ val es vacío")
def step_train_val(context):
    assert context["result"]["intersection_train_val"] == 0


@then("train ∩ test es vacío")
def step_train_test(context):
    assert context["result"]["intersection_train_test"] == 0


@then("val ∩ test es vacío")
def step_val_test(context):
    assert context["result"]["intersection_val_test"] == 0


@then("la unión de los tres es el set de imágenes del dataset (las que entran al split)")
def step_union_all(context):
    assert context["result"]["union_matches_dataset"] is True


@given("pares pHash del analizador")
def step_phash_pairs(context):
    pass


@then("para cada par ambas imágenes están en el mismo split")
def step_pairs_same_split(context):
    assert context["result"]["leaked_pairs"] == 0


@given("un fixture donde el splitter ignorara pHash")
def step_bad_fixture(context):
    context["splits"] = context["bad_splits"]


@then("el test de fuga falla")
def step_fuga_falla(context):
    from dataset_splitting.leakage import analyze_leakage

    bad_result = analyze_leakage(context["splits"], context["all_images"], context["phash_pairs"])
    assert bad_result["leaked_pairs"] > 0
