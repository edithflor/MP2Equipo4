from dataset_quality.mcp.provider import call_provider_safely


def test_provider_success():
    result = call_provider_safely(lambda: "respuesta")

    assert result["ok"] is True
    assert result["response"] == "respuesta"


def test_provider_error_does_not_expose_traceback():
    def broken_provider():
        raise RuntimeError("secret internal provider failure")

    result = call_provider_safely(broken_provider)

    assert result["ok"] is False
    assert result["error"] == "provider_unavailable"
    assert "traceback" not in str(result).lower()
    assert "secret internal provider failure" not in str(result)

