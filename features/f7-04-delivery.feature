Feature: Entrega

Scenario: M1 README
  Given clon fresco y volúmenes borrados
  When sigo el README sin improvisar
  Then app, MariaDB y MinIO quedan arriba
  
Scenario: M2 secretos
  When reviso git log --all de .env y AKIA
  Then no hay credenciales reales ni tfstate tracked
  
Scenario: gitignore
  Then git ls-files no lista .env, pycache, .venv, .dvc/cache, .tfstate, node_modules, jpg/png de dataset
  
Scenario: equipo
  Then git shortlog -sne --all muestra a las 3 personas