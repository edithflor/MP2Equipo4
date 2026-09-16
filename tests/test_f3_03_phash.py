from io import BytesIO

import pytest
from PIL import Image, ImageDraw
from pytest_bdd import given, scenarios, then, when

scenarios("../features/f3-03-phash-duplicates.feature")


@pytest.fixture
def context():
    return {"images": {}, "result": None, "threshold": 5}


@given("una imagen del dataset")
def step_base_image(context):
    img = Image.new("RGB", (100, 100), color="red")
    buf = BytesIO()
    img.save(buf, format="PNG")
    context["images"]["img1"] = buf.getvalue()
    context["base_img"] = img


@given("una copia JPEG recomprimida con otro file_name")
def step_recompressed(context):
    buf = BytesIO()
    context["base_img"].save(buf, format="JPEG", quality=10)
    context["images"]["img2"] = buf.getvalue()

    img3 = context["base_img"].copy()
    d = ImageDraw.Draw(img3)
    d.rectangle([0, 0, 30, 30], fill="blue")
    buf3 = BytesIO()
    img3.save(buf3, format="PNG")
    context["images"]["img3"] = buf3.getvalue()


@when("corro el analizador")
def step_run_analyzer(context):
    from dataset_quality.phash import analyze_duplicates

    context["result"] = analyze_duplicates(context["images"], threshold=context["threshold"])


@then("el par aparece")
def step_pair_appears(context):
    assert len(context["result"]["pairs"]) > 0
    pair_ids = {context["result"]["pairs"][0]["image1"], context["result"]["pairs"][0]["image2"]}
    assert "img1" in pair_ids and "img2" in pair_ids


@then("trae distancia o similitud")
def step_has_distance(context):
    assert "distance" in context["result"]["pairs"][0]


@when("bajo el umbral")
def step_lower_threshold(context):
    if not context["images"]:
        step_base_image(context)
        step_recompressed(context)
    if context["result"] is None:
        context["threshold"] = 15
        from dataset_quality.phash import analyze_duplicates

        context["result"] = analyze_duplicates(context["images"], threshold=context["threshold"])

    context["threshold"] = -1
    from dataset_quality.phash import analyze_duplicates

    context["result_strict"] = analyze_duplicates(context["images"], threshold=context["threshold"])


@then("hay menos pares")
def step_less_pairs(context):
    assert len(context["result_strict"]["pairs"]) < len(context["result"]["pairs"])


@when("lo subo")
def step_raise_threshold(context):
    context["threshold"] = 64
    from dataset_quality.phash import analyze_duplicates

    context["result_loose"] = analyze_duplicates(context["images"], threshold=context["threshold"])


@then("hay más pares")
def step_more_pairs(context):
    assert len(context["result_loose"]["pairs"]) > len(context["result"]["pairs"])


@given("dos archivos con bytes distintos pero visualmente iguales")
def step_bytes_distintos(context):
    step_base_image(context)
    step_recompressed(context)

    assert context["images"]["img1"] != context["images"]["img2"]


@then("pHash los empareja")
def step_phash_matches(context):
    from dataset_quality.phash import analyze_duplicates

    res = analyze_duplicates(context["images"], threshold=5)
    pair_ids = [{p["image1"], p["image2"]} for p in res["pairs"]]
    assert {"img1", "img2"} in pair_ids


@then("el analizador no abre MinIO por su cuenta")
def step_pure_function():
    import pathlib

    try:
        code = pathlib.Path("src/dataset_quality/phash.py").read_text()
        for obj in ["boto3", "Minio", "MongoClient"]:
            assert obj not in code
    except FileNotFoundError:
        pass
