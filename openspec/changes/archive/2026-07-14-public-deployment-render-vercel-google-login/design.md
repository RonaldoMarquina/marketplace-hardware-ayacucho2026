## Context

La base de datos remota en TiDB Cloud Starter ya fue validada y el proyecto
cuenta con frontend React/Vite y backend Flask listos para integrarse con una
salida publica. El backend ya contempla variables de entorno para `DATABASE_URL`,
`FRONTEND_URL`, secretos JWT, correo SMTP y endurecimiento parcial de sesion en
produccion, pero todavia no existe una definicion operativa completa para
Render, Vercel y el comportamiento esperado en una publicacion academica de bajo
costo.

Tambien existe una restriccion de alcance importante: la app ya funciona con
registro, verificacion por correo y login tradicional. `Google login` puede
aportar comodidad, pero no debe bloquear la primera salida publica ni romper el
flujo actual de autenticacion.

Ademas, el backend hoy sirve uploads desde el filesystem local. En un despliegue
gratuito eso introduce una limitacion operativa para permanencia de imagenes y
evidencias, especialmente si la instancia se reinicia o se vuelve a desplegar.

## Goals / Non-Goals

**Goals:**

- definir una ruta de despliegue publico con frontend en Vercel y backend en
  Render conectado a TiDB Cloud
- establecer configuracion minima de produccion para dominios publicos,
  variables de entorno, CORS, secretos y correo real
- dejar documentado el comportamiento aceptado de uploads y medios durante una
  demo academica de bajo costo
- preparar el sistema para agregar `Google login` de forma opcional y
  compatible con el login actual
- habilitar una checklist reproducible de validacion post-despliegue

**Non-Goals:**

- no reemplazar el login actual por `Google login`
- no exigir `Google login` como prerrequisito de despliegue
- no migrar en este cambio a almacenamiento object storage dedicado para medios
- no redisenar toda la infraestructura a un nivel empresarial o multi-entorno

## Decisions

### 1. Separar frontend y backend en plataformas distintas

El frontend se desplegara en Vercel y el backend en Render, manteniendo TiDB
Cloud como base de datos remota principal.

Alternativas consideradas:

- desplegar frontend y backend juntos en una sola plataforma
- retrasar el despliegue hasta contar con infraestructura paga

Razones para no elegirlas:

- la primera reduce flexibilidad y no aprovecha bien el modelo habitual de
  Vercel para frontend estatico
- la segunda contradice la necesidad academica de publicar con costo minimo

### 2. Tratar `Google login` como extension opcional y desacoplada

La salida publica inicial mantendra correo/password como flujo base. Si se
implementa `Google login`, debera convivir con el flujo actual, reutilizar la
cuenta existente cuando corresponda y depender de secretos OAuth y callback URLs
de produccion bien definidos.

Alternativas consideradas:

- exigir `Google login` antes del despliegue
- posponer toda discusion de `Google login`

Razones para no elegirlas:

- la primera retrasa una salida publica que ya puede operar con login
  tradicional
- la segunda deja sin contrato tecnico una integracion que el equipo ya
  considera relevante para la etapa final

### 3. Usar configuracion de produccion estricta en backend

El backend en Render debera arrancar con `DATABASE_URL`, `FRONTEND_URL`,
secretos de aplicacion/JWT, configuracion real de correo y origenes permitidos
alineados con el dominio publico del frontend.

Alternativas consideradas:

- mantener configuracion flexible de desarrollo en produccion
- permitir produccion publica con correo no real o URLs locales residuales

Razones para no elegirlas:

- la primera abre fallas de seguridad y errores de integracion entre dominios
- la segunda contradice reglas ya activas de `auth-security` para produccion
  publica

### 4. Aceptar una primera salida publica con limitacion operativa de medios

Mientras no exista object storage externo, el sistema puede salir a una demo
publica con uploads en disco local del backend, siempre que la documentacion
deje claro que la persistencia de medios no esta garantizada ante reinicios o
redeploys.

Alternativas consideradas:

- bloquear completamente el despliegue hasta integrar almacenamiento externo
- ignorar la limitacion y presentar el despliegue como totalmente durable

Razones para no elegirlas:

- la primera introduce trabajo adicional que puede exceder el objetivo academico
  inmediato
- la segunda crea una expectativa falsa sobre continuidad de imagenes y
  evidencias

### 5. Formalizar una checklist de validacion post-release

El despliegue no se considerara listo solo por levantar servicios. Se validaran
registro, verificacion por correo, login, creacion de anuncios, carga/lectura
de medios, panel admin y conectividad entre frontend, backend y TiDB.

Alternativas consideradas:

- validar solo el arranque tecnico del backend
- validar solo el frontend contra mocks

Razones para no elegirlas:

- la primera no garantiza que la app realmente funcione como sistema integrado
- la segunda no prueba el entorno publico real

## Risks / Trade-offs

- [Uploads en filesystem local pueden perderse tras redeploy] -> Mitigar con
  documentacion explicita, dataset controlado para demo y futura migracion a
  almacenamiento externo
- [CORS o URLs de frontend/backend mal configuradas] -> Mitigar con variables de
  entorno unicas por entorno y validacion completa post-release
- [Correo real bloquea salida publica si no esta bien configurado] -> Mitigar
  con checklist previa y pruebas de registro/verificacion antes de anunciar la
  URL publica
- [Google login agrega complejidad de OAuth y manejo de cuentas duplicadas] ->
  Mitigar tratandolo como extension opcional con rollout separado del go-live
- [Servicios gratuitos pueden suspender, dormir o limitar recursos] -> Mitigar
  con expectativas operativas realistas y foco en demo academica, no SLA alto

## Migration Plan

1. definir variables de entorno finales para backend en Render y frontend en
   Vercel
2. desplegar backend apuntando a TiDB Cloud y validar salud basica del servicio
3. desplegar frontend con la URL publica real del backend
4. ejecutar checklist funcional completa en entorno publico
5. documentar limitaciones conocidas de medios y operacion gratuita
6. dejar `Google login` listo como fase siguiente o integracion opcional si el
   tiempo del proyecto lo permite

Rollback:

- mantener posibilidad de volver temporalmente a entorno local para demo interna
- preservar TiDB Cloud como fuente de datos validada
- retirar frontend publico o backend publico si una configuracion insegura o
  incompleta afecta la demo

## Open Questions

- si Render se usara solo para API o tambien para servir uploads durante la demo
- si el dominio publico final sera el generado por plataforma o uno propio
- si `Google login` se implementara dentro de este cambio o se dejara solo
  especificado para una iteracion posterior
- si hace falta una capa adicional de almacenamiento externo para medios antes de
  la presentacion final
