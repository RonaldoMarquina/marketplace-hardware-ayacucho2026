# Seguridad - HardwareAyacucho

## Autenticacion y autorizacion

- JWT para rutas protegidas
- control de rol `ADMIN` en rutas administrativas
- identidad del usuario obtenida desde el token, no desde el body

## Contraseñas

- hash con bcrypt
- nunca retornar `password_hash`
- mensajes de error consistentes para evitar enumeracion de usuarios

## Tokens

- verificacion y recuperacion con tokens de un solo uso
- expiracion controlada por tipo de token
- invalidacion de tokens anteriores cuando el flujo lo requiere

## Rate limiting

Se aplican limites en flujos sensibles como:

- login
- reenvio de verificacion

## Seguridad de archivos

- validacion de tipo real de archivo
- rutas almacenadas como relativas
- nombres internos controlados por el sistema
- limites de tamano segun modulo

## Seguridad de consultas

- acceso a datos via SQLAlchemy o consultas parametrizadas
- sin interpolacion insegura de strings en SQL
- validacion estricta de parametros usados para filtros

## Configuracion sensible

- secrets y credenciales fuera del repositorio
- uso de `.env` para desarrollo
- `.env` excluido del control de versiones

## Analisis estatico de seguridad

- `Bandit` es la revision estatica especializada para el backend Python
- el comando oficial local es `py -m bandit -c backend/bandit.yaml -r backend/app`
- su alcance se limita a `backend/app` para evitar ruido de frontend y artefactos
- la configuracion minima omite `B105` mientras existan falsos positivos
  asociados a mensajes de validacion y mapas de estados HTTP
- `SonarQube` sigue siendo la capa agregadora que consume `backend/coverage.xml`
  y consolida calidad del monorepo

## Buenas practicas vigentes

- no exponer trazas internas en respuestas
- proteger endpoints administrativos con autenticacion y rol
- restringir acceso a datos sensibles segun contexto del usuario
- mantener auditoria de acciones de moderacion y administracion

## Nota

La seguridad operativa debe revisarse junto con PyTest, Pylint, Bandit,
SonarQube y la configuracion real del entorno antes de despliegue.
