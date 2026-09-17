import json

from dataset_quality.split import split_coco


def test_split_crea_train_val_test(tmp_path):
    coco = {
        "images": [
            {"id": 1, "file_name": "1.jpg"},
            {"id": 2, "file_name": "2.jpg"},
            {"id": 3, "file_name": "3.jpg"},
            {"id": 4, "file_name": "4.jpg"},
            {"id": 5, "file_name": "5.jpg"},
            {"id": 6, "file_name": "6.jpg"},
            {"id": 7, "file_name": "7.jpg"},
            {"id": 8, "file_name": "8.jpg"},
            {"id": 9, "file_name": "9.jpg"},
            {"id": 10, "file_name": "10.jpg"},
        ],
        "annotations": [{"id": i, "image_id": i, "category_id": 1} for i in range(1, 11)],
        "categories": [{"id": 1, "name": "example"}],
    }

    coco_path = tmp_path / "coco.json"
    output_dir = tmp_path / "splits"

    coco_path.write_text(json.dumps(coco), encoding="utf-8")

    split_coco(
        coco_path=coco_path,
        output_dir=output_dir,
        train_ratio=0.7,
        val_ratio=0.2,
        seed=42,
    )

    assert (output_dir / "train.json").exists()
    assert (output_dir / "val.json").exists()
    assert (output_dir / "test.json").exists()

    train = json.loads((output_dir / "train.json").read_text())
    val = json.loads((output_dir / "val.json").read_text())
    test = json.loads((output_dir / "test.json").read_text())

    assert len(train["images"]) == 7
    assert len(val["images"]) == 2
    assert len(test["images"]) == 1


def test_split_es_reproducible(tmp_path):
    coco = {
        "images": [{"id": i, "file_name": f"{i}.jpg"} for i in range(1, 11)],
        "annotations": [],
        "categories": [],
    }

    coco_path = tmp_path / "coco.json"
    first = tmp_path / "first"
    second = tmp_path / "second"

    coco_path.write_text(json.dumps(coco), encoding="utf-8")

    split_coco(coco_path, first, seed=42)
    split_coco(coco_path, second, seed=42)

    assert (first / "train.json").read_text() == (second / "train.json").read_text()
