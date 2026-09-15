"""Criterios ejecutables SPEC-TF-01; validate necesita Terraform y acceso al registry."""

import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest
from pytest_bdd import scenarios, then, when

ROOT = Path(__file__).resolve().parents[1]
TF = ROOT / "terraform"
scenarios("../features/tf-01-terraform-modules.feature")


@then("existen módulos de red, cómputo, datos y almacenamiento")
def layers_exist():
    for layer, resource in {
        "network": "aws_vpc",
        "compute": "aws_instance",
        "data": "aws_db_instance",
        "storage": "aws_s3_bucket",
    }.items():
        content = (TF / "modules" / layer / "main.tf").read_text()
        assert f'resource "{resource}"' in content


@then("no es un único main.tf monolítico")
def composed_stack():
    content = (TF / "main.tf").read_text()
    for layer in ("network", "compute", "data", "storage"):
        assert f'module "{layer}"' in content
    assert not re.search(r"^resource\s", content, re.MULTILINE)


@then("hay dev y prod separados")
def environments():
    for env, cidr in (("dev", "10.42.0.0/16"), ("prod", "10.43.0.0/16")):
        content = (TF / "environments" / env / "main.tf").read_text()
        assert re.search(rf'environment\s*=\s*"{env}"', content)
        assert cidr in content


def terraform(*args, directory=TF):
    executable = os.environ.get("TERRAFORM_BIN") or shutil.which("terraform")
    if not executable:
        if os.environ.get("TF01_REQUIRE_TERRAFORM") == "1":
            pytest.fail("Terraform requerido para validar TF-01")
        pytest.skip("Instalar Terraform o definir TERRAFORM_BIN; CI lo exige")
    result = subprocess.run(
        [executable, f"-chdir={directory}", *args], capture_output=True, text=True, timeout=300
    )
    assert result.returncode == 0, result.stdout + result.stderr


@when("corro terraform fmt -check -recursive")
def formatted():
    terraform("fmt", "-check", "-recursive")


@when("corro init sin backend y validate en ambos entornos")
def validated():
    for env in ("dev", "prod"):
        directory = TF / "environments" / env
        terraform(
            "init", "-backend=false", "-input=false", "-lockfile=readonly", directory=directory
        )
        terraform("validate", "-no-color", directory=directory)


@then("terminan 0")
def commands_succeeded():
    # Los pasos anteriores comprueban cada código y muestran el error completo.
    pass


@then("no hay claves AWS en archivos tf")
def no_secrets():
    for path in TF.rglob("*.tf"):
        if ".terraform" not in path.parts:
            content = path.read_text()
            assert "AKIA" not in content, path
            assert "aws_secret_access_key" not in content.lower(), path


@then("tfstate está ignorado y no versionado")
def no_tracked_state():
    tracked = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).splitlines()
    assert not any(".tfstate" in Path(path).name for path in tracked)
    for candidate in (
        "terraform/terraform.tfstate",
        "terraform/environments/dev/test.tfstate",
        "terraform/environments/prod/test.tfstate.backup",
    ):
        result = subprocess.run(["git", "check-ignore", "--quiet", candidate], cwd=ROOT)
        assert result.returncode == 0, candidate
