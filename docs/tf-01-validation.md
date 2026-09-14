# Evidencia SPEC-TF-01

Verificación local: 2026-09-14, Windows AMD64, Terraform 1.9.8, provider AWS 6.64.0.
Rama: `feat/tf-01-terraform-modules`, creada desde `origin/main` en `df5f7d8`.
En la referencia consultada F2-01 todavía no estaba integrado; este ticket es independiente.

## Criterios

| Criterio | Evidencia |
| --- | --- |
| Red, cómputo, datos, almacenamiento | Cuatro módulos con recursos AWS y composición en terraform/main.tf |
| dev/prod separados | environments/dev y environments/prod, estados locales independientes, CIDR y nombres diferentes |
| fmt termina 0 | terraform -chdir=terraform fmt -check -recursive |
| init sin backend y validate terminan 0 | Ejecutados en dev, prod y raíz |
| Sin claves en .tf | Escenario sin secretos aprobado |
| Estado ignorado y no tracked | git check-ignore probado con rutas anidadas y git ls-files sin tfstate |
| Feature ejecutable | Cuatro escenarios de features/tf-01-terraform-modules.feature aprobados |

## Salida de aceptación (extracto de las ejecuciones)

```text
terraform/environments/dev: init -backend=false -input=false -lockfile=readonly
Terraform has been successfully initialized!
terraform/environments/dev: validate -no-color
Success! The configuration is valid.

terraform/environments/prod: init -backend=false -input=false -lockfile=readonly
Terraform has been successfully initialized!
terraform/environments/prod: validate -no-color
Success! The configuration is valid.

terraform: validate -no-color
Success! The configuration is valid.

terraform: test -no-color
run "network_is_private"... pass
run "compute_is_private"... pass
run "production_database"... pass
run "storage_is_versioned"... pass
Success! 4 passed, 0 failed.

pytest -v (TERRAFORM_BIN definido y TF01_REQUIRE_TERRAFORM=1)
9 passed, 1 warning in 12.41s
ruff check .
All checks passed!
ruff format --check .
10 files already formatted
python scripts/check_repo_hygiene.py
Higiene del repositorio: PASS
```

El aviso de pytest fue un permiso local para escribir su caché; no hubo escenarios
omitidos ni pruebas fallidas en esta ejecución. La suite comprende cinco pruebas
preexistentes de main y cuatro escenarios de este ticket.

Se escribieron y ejecutaron primero los escenarios estructurales: dos fallaron
porque las capas y entornos aún no existían. Después de implementarlos pasaron.
Estas ejecuciones no constituyen commits históricos Red/Green.

No se ejecutó apply ni se contactaron APIs AWS para provisionar recursos. Las pruebas
Terraform utilizan proveedor simulado y command=plan. Los checks de GitHub Actions
quedan pendientes de subir esta rama; la evidencia anterior corresponde a ejecución local.
