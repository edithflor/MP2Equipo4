# TF-01 — Módulos y validación

Requiere Terraform >=1.9 y <2.0. Provider AWS 6.x. Módulos:

- `network`: VPC, subred privada, tabla de rutas y endpoint Gateway S3 asociado.
- `storage`: bucket PROD versionado, cifrado AES256, bloqueo público y política TLS.
- `identity`: proveedor GitHub OIDC (o ARN existente), rol limitado al repositorio
  y rama configurados, permisos de objetos únicamente en el prefijo `dvc/`.

## Validación local sin cuenta AWS

Desde esta carpeta:

```sh
terraform fmt -check -recursive
terraform init -backend=false
terraform validate
```

`init` necesita red para descargar el provider; `validate` no crea recursos ni
necesita credenciales. Versionar `.terraform.lock.hcl` para reproducir el provider.
La CI ejecuta estos controles sin claves AWS.

## Configuración para un despliegue posterior

Copiar `terraform.tfvars.example` a `terraform.tfvars` y elegir un nombre de bucket
globalmente único. Si la cuenta ya tiene el proveedor OIDC de GitHub, suministrar
`github_oidc_provider_arn` para reutilizarlo. Usar autenticación temporal/SSO para
provisionar la infraestructura; el rol creado permite datos DVC, no administrar AWS.

En GitHub Actions, un futuro workflow de datos debe solicitar `id-token: write`
y asumir el output `github_role_arn` mediante OIDC. Este ticket no agrega un
workflow de despliegue ni ejecuta `apply`.

El endpoint S3 sirve a cargas dentro de esta VPC. Un runner alojado por GitHub
accede al endpoint público de S3 con TLS y OIDC; no atraviesa esta subred privada.
El remote DEV sigue siendo MinIO local. No se configura DVC ni se transfieren datos aquí.

El estado es local por ahora y está ignorado por Git. Antes de desplegar en equipo
se debe acordar un backend compartido. No subir `.tfstate`, planes ni credenciales.

Referencias oficiales:
- https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/vpc_endpoint
- https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_openid_connect_provider
