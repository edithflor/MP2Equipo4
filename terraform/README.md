# TF-01 — Terraform por capas

Alcance de SPEC-TF-01: cuatro módulos, entornos separados y validación local/CI.
No se requiere una cuenta AWS ni ejecutar apply. OIDC, VPC endpoint y remote state
corresponden a TF-02…04 y no están incluidos en esta configuración.

| Capa | Módulo | Recursos |
| --- | --- | --- |
| Red | `modules/network` | VPC, dos subredes privadas en AZ distintas y rutas |
| Cómputo | `modules/compute` | EC2 privado, grupo de seguridad, disco cifrado, IMDSv2 |
| Datos | `modules/data` | RDS MariaDB privado, subnet group, reglas TCP 3306 desde EC2 |
| Almacenamiento | `modules/storage` | S3 versionado, cifrado y bloqueo público |

`main.tf` compone los módulos. Cada directorio `environments/dev` y
`environments/prod` es una raíz independiente, con su propio lockfile y estado local.
DEV usa la red 10.42.0.0/16 y nombres mp2-dev; PROD usa 10.43.0.0/16 y mp2-prod.
Los buckets deben terminar en -dev/-prod y tener nombres globalmente únicos.
PROD habilita Multi-AZ, retención de siete días y protección de borrado en RDS.

## Validación sin credenciales

Requiere Terraform 1.9.8 (la versión de CI), Python 3.12 y dependencias `.[dev]`.
Desde la raíz del repositorio:

```sh
terraform -chdir=terraform fmt -check -recursive
terraform -chdir=terraform/environments/dev init -backend=false -input=false -lockfile=readonly
terraform -chdir=terraform/environments/dev validate
terraform -chdir=terraform/environments/prod init -backend=false -input=false -lockfile=readonly
terraform -chdir=terraform/environments/prod validate
terraform -chdir=terraform init -backend=false -input=false -lockfile=readonly
terraform -chdir=terraform validate
terraform -chdir=terraform test
```

`init` necesita red para consultar el registry. Los lockfiles contienen los checksums
oficiales para Windows y Linux. Al cambiar la versión del provider, regenerarlos
en cada raíz con `terraform providers lock -platform=windows_amd64 -platform=linux_amd64`.

El feature `features/tf-01-terraform-modules.feature` es ejecutable:

```sh
pytest tests/test_terraform_feature.py -v
```

Si Terraform no está en PATH se puede definir `TERRAFORM_BIN` con su ruta absoluta.
Sin el ejecutable, pytest omite solo el escenario de comandos; CI define
`TF01_REQUIRE_TERRAFORM=1` para que su ausencia sea un error. Los comandos se ejecutan
de verdad y se comprueban sus códigos. `terraform test` usa mocks y operaciones plan,
sin crear infraestructura. El workflow Terraform ejecuta todos estos controles.

## Valores para un futuro despliegue

`terraform.tfvars.example` en cada entorno explica los valores requeridos para
plan/apply: AMI Linux x86_64 válida en la región elegida y nombre único del bucket.
Los ejemplos son marcadores, no valores utilizables para despliegue. Cambiar también
las zonas si se cambia de región. Validate no requiere estos valores.

RDS administra la contraseña maestra mediante Secrets Manager; no hay contraseña
en archivos .tf. La aplicación aún no se instala en EC2: empaquetado, acceso operativo
y permisos de ejecución se resolverán en tickets posteriores. La instancia no tiene
IP pública, SSH abierto, NAT ni acceso a S3 en esta fase. No es una app desplegada.

No versionar tfstate, .terraform, tfvars reales ni planes. El estado remoto está fuera
de alcance. Separar los directorios no autoriza desplegarlos sin revisar costos,
valores y acceso al estado con el equipo.

Evidencia local: `docs/tf-01-validation.md` en la raíz del repositorio.
Referencias: https://developer.hashicorp.com/terraform/language/tests/mocking
