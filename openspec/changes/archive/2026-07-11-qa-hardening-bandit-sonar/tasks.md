## 1. Preparacion de herramientas

- [x] 1.1 Agregar `Bandit` a las dependencias del backend o dejar definida su
  instalacion de trabajo local
- [x] 1.2 Definir el comando oficial de ejecucion de `Bandit` para el backend
- [x] 1.3 Revisar que el flujo actual de cobertura siga generando
  `backend/coverage.xml` para SonarQube

## 2. Endurecimiento de QA local

- [x] 2.1 Incorporar `Bandit` al flujo documentado de validacion local
- [x] 2.2 Ajustar scripts, configuraciones o comandos de soporte para ejecutar
  PyTest, cobertura, Pylint, Bandit y SonarQube en orden coherente
- [x] 2.3 Resolver o documentar hallazgos iniciales de seguridad estatica que
  bloqueen el flujo minimo

## 3. Documentacion tecnica

- [x] 3.1 Actualizar `docs/TESTING.md` con el flujo completo de QA hardening
- [x] 3.2 Actualizar `docs/SECURITY.md` con el rol de Bandit y SonarQube dentro
  del endurecimiento del backend
- [x] 3.3 Ajustar la metodologia o documentos relacionados si el flujo final
  cambia respecto a la secuencia actualmente descrita

## 4. Validacion y cierre

- [x] 4.1 Ejecutar pruebas necesarias para confirmar que el flujo de QA no rompe
  la suite existente
- [x] 4.2 Ejecutar el analisis estatico definido y registrar el resultado
  esperado del nuevo flujo
- [x] 4.3 Dejar el cambio listo para sincronizacion o archivo en OpenSpec una
  vez implementado
