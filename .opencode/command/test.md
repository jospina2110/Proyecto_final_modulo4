---
description: Ejecuta la suite de pruebas del backend y reporta resultados
agent: qa
subagent: true
---

Ejecuta la suite de pruebas del backend (`pytest` con working dir `backend/`,
con las dependencias instaladas; el contenedor del backend no copia `tests/`).

Reporta:

- Resultado por archivo de prueba (pasadas/fallidas).
- Para cada fallo: causa raíz, pasos de reproducción y severidad.
- Riesgos si no se pudieron ejecutar (por ejemplo, MongoDB no disponible).
- Veredicto: apto o no apto para continuar.

Contexto adicional: $ARGUMENTS
