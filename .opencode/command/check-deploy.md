---
description: Checklist pre-despliegue antes de publicar imágenes en Docker Hub
agent: devops
subagent: true
---

Ejecuta la checklist pre-despliegue del proyecto:

1. Pruebas en verde (`pytest` en `backend/`).
2. `docker compose config` y `docker compose build` válidos.
3. Variables de entorno correctas: `.env` fuera del repositorio,
   `.env.example` como única plantilla, `DOCKERHUB_TOKEN` solo en GitHub Secrets.
4. Tags de imagen versionados (`IMAGE_VERSION` + `sha` del commit).
5. Rollback confirmado: cómo volver a la versión previa por tag.
6. El backend sigue sin estar publicado al host (solo frontend en 8080).

Reporta bloqueos, riesgos y el veredicto final. Recuerda: la publicación real
requiere aprobación humana explícita.

Contexto adicional: $ARGUMENTS
