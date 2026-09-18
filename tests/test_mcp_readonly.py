from dataset_quality.mcp.server import (
    get_dataset_versions,
    get_quality_report,
    get_version_diff,
    mcp,
)


def test_mcp_server_name():
    assert mcp.name == "dataset-quality-readonly"


def test_tools_are_callable():
    assert callable(get_quality_report)
    assert callable(get_dataset_versions)
    assert callable(get_version_diff)


def test_missing_file_returns_controlled_error(tmp_path):
    missing = tmp_path / "missing.json"

    result = get_quality_report(str(missing))

    assert result["error"] == "file_not_found"
    assert result["path"] == str(missing)
