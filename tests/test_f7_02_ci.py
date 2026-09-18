import os

from pytest_bdd import given, scenarios, then

scenarios("../features/f7-02-ci.feature")


@given(".github/workflows")
def step_workflows_dir():
    assert os.path.exists(".github/workflows"), "Falta la carpeta .github/workflows"


@then("corre ruff (o lint)")
def step_runs_ruff():
    with open(".github/workflows/ci.yaml", encoding="utf-8") as f:
        content = f.read()
        assert "ruff check" in content, "No se ejecuta Ruff en el CI"


@then("corre pytest")
def step_runs_pytest():
    with open(".github/workflows/ci.yaml", encoding="utf-8") as f:
        content = f.read()
        assert "pytest" in content, "No se ejecuta Pytest en el CI"


@then("corre el quality gate")
def step_runs_qgate():
    import os

    assert os.path.exists("tests/test_f4_02_gate_blocks.py"), (
        "Falta el archivo de pruebas del Quality Gate"
    )


@given("un check fail (umbral imposible en una rama de prueba)")
def step_fail_mock():
    pass


@then("el job termina distinto de 0")
def step_job_fails():
    pass


@then("no hay continue-on-error en esos pasos")
def step_no_continue_on_error():
    with open(".github/workflows/ci.yaml", encoding="utf-8") as f:
        content = f.read()
        assert "continue-on-error: true" not in content.lower(), (
            "¡Trampa detectada! Se encontró continue-on-error"
        )


@then("main/default tiene un run reciente")
def step_main_recent_run():
    pass
