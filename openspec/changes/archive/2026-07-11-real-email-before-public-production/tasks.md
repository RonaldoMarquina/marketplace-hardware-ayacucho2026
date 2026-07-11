## 1. Configuracion de correo real

- [x] 1.1 Definir variables de entorno y modo de ejecucion para proveedor de
  correo transaccional
- [x] 1.2 Crear un adaptador o servicio de envio reutilizable para backend
- [x] 1.3 Documentar el criterio de “correo real obligatorio antes de
  produccion publica”

## 2. Integracion en autenticacion

- [x] 2.1 Reemplazar el envio basado en logs en verificacion de correo por el
  adaptador real
- [x] 2.2 Reemplazar el envio basado en logs en reset password por el adaptador
  real
- [x] 2.3 Mantener un comportamiento seguro para testing y desarrollo local sin
  proveedor externo obligatorio

## 3. Validacion y documentacion

- [x] 3.1 Agregar o ajustar pruebas para los flujos de envio de verificacion y
  reset password
- [x] 3.2 Actualizar documentacion tecnica y de despliegue con precondiciones de
  correo real
- [x] 3.3 Dejar explicitamente `Google login` como cambio posterior, fuera de
  este alcance
