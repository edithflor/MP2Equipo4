from collections.abc import Callable


def call_provider_safely(
    provider_call: Callable[[], str],
) -> dict[str, str | bool]:
    try:
        response = provider_call()
        return {
            "ok": True,
            "response": response,
        }
    except Exception:
        return {
            "ok": False,
            "error": "provider_unavailable",
            "message": "El proveedor de Copilot no está disponible.",
        }

