## 1. Tokens y persistencia

- [x] 1.1 Definir una estrategia para no persistir el token de reset reusable en
  claro
- [x] 1.2 Ajustar modelo, repositorio y servicio para validar el nuevo formato
- [x] 1.3 Cubrir compatibilidad y expiracion con pruebas automatizadas

## 2. Sesiones y revocacion

- [x] 2.1 Definir una marca de invalidez para JWT emitidos antes del reset
- [x] 2.2 Aplicar la revocacion de sesiones al confirmar reset password
- [x] 2.3 Probar que tokens autenticados previos ya no sirven despues del cambio

## 3. Abuso y auditoria

- [x] 3.1 Reforzar señales de auditoria del flujo de reset sin filtrar secretos
- [x] 3.2 Revisar y endurecer limites de abuso por IP/correo si hace falta
- [x] 3.3 Actualizar documentacion tecnica con las nuevas garantias de seguridad
