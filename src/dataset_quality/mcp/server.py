import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("dataset-quality-readonly")


def _load_json(path: str) -> dict:
    file_path = Path(path)

    if not file_path.exists():
        return {
            "error": "file_not_found",
            "path": path,
        }

    return json.loads(file_path.read_text(encoding="utf-8"))


@mcp.tool()
def get_quality_report(
    path: str = "data/reports/quality.json",
) -> dict:
    """Return the current dataset quality report from a local JSON artifact."""
    return _load_json(path)


@mcp.tool()
def get_dataset_versions(
    path: str = "metadata/versions.json",
) -> dict:
    """Return the registered semantic dataset versions."""
    return _load_json(path)


@mcp.tool()
def get_version_diff(
    path: str = "metadata/diff-v0.1.0-v1.0.0.json",
) -> dict:
    """Return the stored diff between dataset versions."""
    return _load_json(path)


if __name__ == "__main__":
    mcp.run()
