# AGENTS.md — Contexto compartido del proyecto

Este archivo es la única fuente de verdad del contexto para todos los agentes
(portables en `agents/` y operativos en `.opencode/agent/`). Léelo antes de actuar.

## Descripción

Sistema de Gestión de Citas Médicas: API REST para administrar pacientes,
médicos y citas médicas, con frontend web, MongoDB, contenedores Docker,
publicación de imágenes en Docker Hub y pipeline CI/CD con GitHub Actions.

## Stack

| Componente | Tecnología |
|---|---|
| Backend | Python 3.12 + FastAPI (async) |
| Acceso a datos | Beanie (ODM, `beanie>=1.27.0,<2.0.0`) + Motor sobre MongoDB 7 |
| Validación | Pydantic v2 + pydantic-settings |
| Frontend | HTML, CSS y JavaScript vanilla, servido con nginx (proxy `/api`) |
| Pruebas | pytest + pytest-asyncio + mongomock-motor + httpx |
| Contenedores | Docker + Docker Compose |
| CI/CD | GitHub Actions (pruebas → build y publicación en Docker Hub) |

## Estructura

```
backend/
├── app/
│   ├── main.py            # App FastAPI, routers, lifespan (init de BD)
│   ├── config/            # settings y conexión a MongoDB
│   ├── models/            # Documentos Beanie: Patient, Doctor, Appointment
│   ├── schemas/           # DTOs Pydantic de entrada y salida
│   ├── routes/            # Endpoints HTTP (pacientes, médicos, citas)
│   ├── services/          # Reglas de negocio
│   ├── repositories/      # Única capa que consulta y escribe en MongoDB
│   ├── middlewares/       # Manejo global de errores (404, 409, 500)
│   └── utils/             # Excepciones de dominio
├── scripts/seed.py        # Datos ficticios: 20 pacientes, 4 médicos, 20 citas
└── tests/                 # pytest con mongomock-motor
frontend/                  # Imágenes propias: Dockerfile, nginx.conf, public/
docs/                      # Cuestionario, diagramas Mermaid y evidencias
agents/                    # Agentes portables: roles y responsabilidades (Markdown)
.opencode/                 # Agentes operativos y comandos para opencode
opencode.json              # Configuración de opencode (agente por defecto e instrucciones)
.github/workflows/ci-cd.yml  # Job test → job publish (main); publish usa environment dockerhub
docker-compose.yml         # mongo + backend + frontend en app_network
```

## Convenciones de arquitectura

- Flujo de capas: `routes` (HTTP) → `services` (negocio) → `repositories`
  (MongoDB) → `models` (documentos Beanie).
- `schemas` valida entrada/salida; nunca se confía en datos sin validar.
- `routes` no contiene lógica de negocio; los `services` no hablan HTTP.
- `middlewares` traduce excepciones de dominio a respuestas HTTP (404, 409, 500).
- Cancelar una cita (`DELETE /appointments/{id}`) conserva el historial: es una
  cancelación lógica, no un borrado físico.
- Máquina de estados de la cita: `PENDING → CONFIRMED → COMPLETED`, con paso a
  `CANCELLED` desde `PENDING` o `CONFIRMED`; `COMPLETED` y `CANCELLED` son
  terminales. Repetir el mismo estado es idempotente; transiciones inválidas,
  solapamientos de agenda del médico y duplicados de paciente
  (`email`/`document_id`) responden 409.
- El frontend consume la API vía proxy nginx en `/api`; nunca accede a MongoDB.
- El backend no se publica al host: solo es accesible dentro de `app_network`.

## Comandos

| Acción | Comando |
|---|---|
| Levantar todo | `docker compose up --build -d` |
| Datos de ejemplo | `docker compose exec backend python -m scripts.seed` |
| Pruebas | `cd backend` y `pytest` (con dependencias instaladas; el contenedor no incluye `tests/`) |
| Desarrollo local | `uvicorn app.main:app --reload` (MongoDB en `localhost:27017`) |

| URL | Dirección |
|---|---|
| Frontend | http://localhost:8080 |
| Swagger | http://localhost:8080/docs |
| API vía proxy | http://localhost:8080/api/patients |

## Definition of Done (global)

1. Las pruebas pasan (`pytest` en `backend/`).
2. Sin secretos ni credenciales en el repositorio.
3. Errores manejados con excepciones de dominio, sin trazas expuestas.
4. Documentación actualizada si cambian contratos (README, `docs/`).
5. El proyecto sigue levantando con `docker compose up --build -d`.

## Seguridad y secretos

- `.env` no se versiona; `.env.example` es la plantilla.
- `DOCKERHUB_TOKEN` vive únicamente como secreto de GitHub Actions.
- Variables de entorno del stack: `MONGO_URI`, `MONGO_DB`, `DOCKERHUB_USERNAME`,
  `FRONTEND_BIND` (por defecto `127.0.0.1`).
- Hallazgo abierto SEC-01: la API no implementa autenticación (riesgo conocido y
  acotado por el alcance académico). Mitigación planificada en
  `docs/plan-autenticacion.md`; Fase 0 ya aplicada: el frontend solo se publica
  en loopback.

## Protocolo de agentes

- Orquestación: `@Architect` analiza, decide y delega; los especialistas no
  invaden dominios ajenos y no se pisan entre sí.
- Escalado al humano obligatorio ante: cambios destructivos, migraciones de
  datos, uso de credenciales, publicación de imágenes o decisiones de
  arquitectura que cambien contratos.
- Contrato de handoff: toda tarea termina con este formato.

```
## Resultado
- Resumen: qué se hizo y por qué
- Archivos modificados: rutas exactas
- Riesgos / impacto: en qué puede fallar o afectar
- Siguiente paso sugerido: agente o acción recomendada
```
