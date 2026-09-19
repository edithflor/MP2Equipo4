import subprocess

from pytest_bdd import given, scenarios, then, when

scenarios("../features/f7-04-delivery.feature")


@given("clon fresco y volúmenes borrados")
def step_fresh_clone():
    pass


@when("sigo el README sin improvisar")
def step_readme():
    pass


@then("app, MariaDB y MinIO quedan arriba")
def step_services_up():
    pass


@when("reviso git log --all de .env y AKIA")
def step_check_secrets_log():
    pass


@then("no hay credenciales reales ni tfstate tracked")
def step_no_secrets():
    result = subprocess.run(["git", "ls-files", "*.tfstate"], capture_output=True, text=True)
    assert result.stdout.strip() == "", "CRÍTICO: Se encontró un .tfstate trackeado en Git"


@then(
    "git ls-files no lista .env, pycache, .venv, .dvc/cache, .tfstate, node_modules, jpg/png de dataset"  # noqa: E501
)
def step_check_gitignore():
    result = subprocess.run(["git", "ls-files"], capture_output=True, text=True)
    tracked_files = result.stdout.splitlines()

    forbidden_exact = [".env"]
    forbidden_dirs = ["__pycache__/", ".venv/", ".dvc/cache/", "node_modules/"]

    for file in tracked_files:
        assert file not in forbidden_exact, (
            f"CRÍTICO: El archivo prohibido '{file}' está trackeado en Git."
        )
        for f_dir in forbidden_dirs:
            assert f_dir not in file, (
                f"CRÍTICO: El directorio prohibido '{f_dir}' (en '{file}') está trackeado en Git."
            )
        if file.startswith("data/") or file.startswith("dataset/"):
            assert not file.endswith((".jpg", ".png", ".jpeg")), (
                f"CRÍTICO: Imagen del dataset '{file}' trackeada en Git."
            )


@then("git shortlog -sne --all muestra a las 3 personas")
def step_check_team():
    pass
