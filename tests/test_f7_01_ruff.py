import os
import subprocess

from pytest_bdd import scenarios, then, when

scenarios("../features/f7-01-ruff.feature")


@then("ruff está en pyproject.toml o ruff.toml")
def step_config_exists():
    assert os.path.exists("pyproject.toml") or os.path.exists("ruff.toml"), (
        "No se encontró configuración de Ruff"
    )


@then("hay reglas elegidas por el equipo")
def step_rules_exist():
    config_file = "pyproject.toml" if os.path.exists("pyproject.toml") else "ruff.toml"
    with open(config_file, encoding="utf-8") as f:
        content = f.read()
        assert "[tool.ruff" in content
        assert "select" in content or "ignore" in content or "line-length" in content


@when("corro ruff check .")
def step_run_check():
    pass


@when("ruff format --check .")
def step_run_format():
    pass


@then("ambos terminan 0")
def step_both_zero():
    check_result = subprocess.run(["ruff", "check", "."], capture_output=True, text=True)
    format_result = subprocess.run(
        ["ruff", "format", "--check", "."], capture_output=True, text=True
    )

    assert check_result.returncode == 0, (
        f"Ruff check falló:\n{check_result.stdout}\n{check_result.stderr}"
    )
    assert format_result.returncode == 0, (
        f"Ruff format falló:\n{format_result.stdout}\n{format_result.stderr}"
    )
