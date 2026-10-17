# Sistema de Gestión de Citas Médicas

API REST para administrar pacientes, médicos y citas médicas, con frontend web, base de datos MongoDB, contenedores Docker, publicación de imágenes en Docker Hub y pipeline CI/CD con GitHub Actions.

> **Nota de seguridad (SEC-01):** la API **no implementa autenticación**; es un riesgo aceptado y acotado por el alcance académico. El frontend se publica solo en loopback (`127.0.0.1`) como contención. Antes de exponer el sistema fuera de localhost debe ejecutarse el plan descrito en [`docs/plan-autenticacion.md`](docs/plan-autenticacion.md).

## Stack

| Componente | Tecnología |
|---|---|
| Backend | Python 3.12 + FastAPI |
| Acceso a datos | Beanie (ODM) + Motor; dependencia fijada `beanie>=1.27.0,<2.0.0` |
| Base de datos | MongoDB 7 |
| Frontend | HTML, CSS y JavaScript servidos con nginx |
| Orquestación | Docker Compose |
| CI/CD | GitHub Actions |

## Estructura del proyecto

```
Proyecto_final_pool/
├── backend/                  # API REST (FastAPI + Beanie)
│   ├── app/
│   │   ├── main.py           # Aplicación FastAPI, routers y ciclo de vida
│   │   ├── config/           # Configuración y conexión a MongoDB
│   │   ├── models/           # Documentos: Patient, Doctor, Appointment
│   │   ├── schemas/          # DTOs de entrada y salida
│   │   ├── routes/           # Endpoints HTTP
│   │   ├── services/         # Reglas de negocio
│   │   ├── repositories/     # Acceso a datos (única capa que consulta la BD)
│   │   ├── middlewares/      # Manejo global de errores
│   │   └── utils/            # Excepciones de dominio
│   ├── scripts/seed.py       # Datos ficticios: 20 pacientes, 4 médicos, 20 citas
│   └── tests/                # Pruebas con pytest
├── frontend/                 # Interfaz web (segunda imagen propia)
├── docs/
│   ├── cuestionario/         # Preguntas teóricas por parte
│   ├── diagramas/            # Diagramas Mermaid (clases, arquitectura, despliegue)
│   └── evidencias/           # Capturas de Docker Hub y del pipeline
├── agents/                   # Agentes portables: roles y responsabilidades
├── .opencode/                # Agentes operativos y comandos del entorno de agentes
├── opencode.json             # Configuración de opencode: agente por defecto e instrucciones
├── .github/workflows/        # Pipeline CI/CD
└── docker-compose.yml        # Backend + frontend + MongoDB
```

### Responsabilidad de los componentes

| Componente | Responsabilidad |
|---|---|
| `backend/app/routes` | Recibir peticiones HTTP, delegar en servicios y definir códigos de estado |
| `backend/app/services` | Reglas de negocio (por ejemplo, evitar citas simultáneas del mismo médico) |
| `backend/app/repositories` | Única capa autorizada para consultar y escribir en MongoDB |
| `backend/app/models` | Documentos MongoDB (Patient, Doctor, Appointment) |
| `backend/app/schemas` | Validación de datos de entrada y formato de salida |
| `backend/app/middlewares` | Traducir excepciones de dominio a respuestas HTTP (404, 409, 500) |
| `frontend` | Interfaz web que consume la API a través del proxy nginx (`/api`) |
| `.github/workflows` | Instalar dependencias, ejecutar pruebas y publicar imágenes |

## Puesta en marcha

```bash
docker compose up --build -d
docker compose exec backend python -m scripts.seed
```

| Servicio | URL |
|---|---|
| Frontend | http://localhost:8080 |
| Swagger (documentación de la API) | http://localhost:8080/docs |
| API a través del proxy | http://localhost:8080/api/patients |

### Exposición del frontend (`FRONTEND_BIND`)

El puerto del frontend se publica **solo en loopback** por defecto:

```yaml
ports:
  - "${FRONTEND_BIND:-127.0.0.1}:8080:80"
```

- **Valor por defecto (`127.0.0.1`)**: el frontend solo es accesible desde la propia máquina. Es la Fase 0 de contención aplicada mientras la API no tiene autenticación (ver `docs/plan-autenticacion.md`).
- **Acceso desde la LAN**: `FRONTEND_BIND=0.0.0.0 docker compose up -d`. Hazlo solo de forma consciente del riesgo: sin autenticación, toda la API queda expuesta al resto de la red (SEC-01).

## Endpoints principales

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/patients` | Registrar paciente |
| GET | `/patients` | Consultar pacientes |
| POST | `/doctors` | Registrar médico |
| GET | `/doctors` | Consultar médicos |
| POST | `/appointments` | Programar cita médica |
| GET | `/appointments?status=&date=&patient_id=&doctor_id=` | Consultar citas con filtros |
| GET | `/appointments/{id}` | Consultar una cita específica |
| PATCH | `/appointments/{id}/status` | Actualizar estado de una cita (ver máquina de estados) |
| DELETE | `/appointments/{id}` | Cancelar cita conservando el historial (ver máquina de estados) |
| GET | `/health` | Estado del servicio (`{"status": "ok"}`); interno (nginx no lo proxifica) |

### Máquina de estados de las citas

```text
PENDING ──► CONFIRMED ──► COMPLETED   (terminal)
   │            │
   └────────────┴──────► CANCELLED    (terminal)
```

- **Transiciones permitidas**: `PENDING → CONFIRMED`, `PENDING → CANCELLED`, `CONFIRMED → COMPLETED`, `CONFIRMED → CANCELLED`. `COMPLETED` y `CANCELLED` son **estados terminales**: ninguna transición sale de ellos.
- **Idempotencia**: `PATCH` con el estado actual no modifica nada y responde `200`; cancelar dos veces una cita ya cancelada (`DELETE`) tampoco falla.
- **Error 409**: transición no permitida (por ejemplo, `COMPLETED → CANCELLED`), solapamiento de agenda del mismo médico o paciente duplicado por `email`/`document_id`.
- **Error 404**: paciente, médico o cita inexistente.

## Desarrollo local (sin Docker)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m scripts.seed
uvicorn app.main:app --reload
```

Requiere MongoDB local en `mongodb://localhost:27017` (valor por defecto) o la variable `MONGO_URI` en un archivo `.env`.

## CI/CD (GitHub Actions)

El pipeline (`.github/workflows/ci-cd.yml`) tiene dos jobs:

1. **`test`**: en cada push a `main` y en cada pull request instala las dependencias y ejecuta `pytest`.
2. **`publish`**: solo en push a `main` y tras pasar `test`; construye y publica las imágenes del backend y del frontend en Docker Hub (tags `v1.0` y el `sha` del commit).

El job `publish` usa `environment: dockerhub`, previsto como gate de aprobación para proteger `DOCKERHUB_TOKEN`. **Paso manual pendiente**: crear ese environment en GitHub (Settings → Environments) con *required reviewers*, para que la publicación requiera aprobación humana; mientras no exista, no hay gate activo.

## Decisiones de diseño

- **MongoDB**: se eligió por la flexibilidad de esquema y la representación natural de documentos; la justificación completa está en `docs/cuestionario/parte1.md` (pregunta 10).
- **Beanie**: la alternativa de acceso a datos compatible con MongoDB está documentada en `docs/cuestionario/parte3.md` (preguntas 44 y 45); Beanie cumple el rol de ODM frente a MongoDB.
- **Python en lugar de Node.js**: es una desviación deliberada del enunciado; el enfoque elegido en Python (Beanie) está documentado en `docs/cuestionario/parte3.md` (preguntas 44 y 45) y se ampliará en la sustentación.
- **Puertos**: el frontend publica `8080:80`; el backend solo expone `8000` dentro de la red de Docker Compose y se consume vía el proxy nginx (diferencia entre exponer y publicar).
- **Secretos**: `DOCKERHUB_TOKEN` vive únicamente como secreto de GitHub Actions; `.env` no se versiona.
