# Plan de autenticación — Riesgo aceptado SEC-01

| Campo | Valor |
|---|---|
| Identificador | SEC-01 |
| Fecha de aceptación | 2026-10-17 |
| Estado | Riesgo aceptado; mitigación planificada |
| Origen | Auditoría de seguridad del agente `@security` |
| Alcance | API REST completa (pacientes, médicos y citas) |

## Descripción del riesgo

La API no implementa autenticación ni autorización: cualquier cliente con
acceso de red puede consultar, crear, modificar y cancelar pacientes, médicos
y citas. El riesgo se acepta de forma temporal porque el proyecto tiene alcance
académico y su exposición está contenida (Fase 0), pero el sistema **no debe
exponerse fuera de localhost** hasta completar la autenticación y su auditoría.

## Fases de mitigación

| Fase | Medida | Estado |
|---|---|---|
| 0 | Contención: frontend publicado solo en `127.0.0.1` | **Ya aplicada** |
| 1 | API key para clientes de confianza | Pendiente |
| 2 | JWT/OAuth2 con roles (administración, recepción, médico) | Pendiente |
| 3 | TLS, rate limiting y auditoría de accesos | Pendiente |

### Fase 0 — Contención (aplicada)

En `docker-compose.yml` el frontend se publica como
`"${FRONTEND_BIND:-127.0.0.1}:8080:80"`: por defecto solo escucha en loopback,
y el backend nunca se publica al host (solo es accesible dentro de
`app_network`). Exponer el frontend en la LAN exigiría
`FRONTEND_BIND=0.0.0.0`, lo que no debe hacerse sin autorización explícita.

### Fase 1 — API key

Emisión de claves para clientes de confianza y validación en el backend.
Adecúa el control de acceso sin introducir todavía identidades de usuario.

### Fase 2 — JWT/OAuth2 + roles

Autenticación de usuarios con JWT/OAuth2 y autorización por roles. Es la fase
que habilita el criterio de salida de este plan.

### Fase 3 — TLS, rate limiting y auditoría

Cifrado del transporte (TLS), limitación de tasa y registro de auditoría de
accesos, antes de cualquier exposición fuera de localhost.

## Criterio de salida

La autenticación debe estar **implementada, probada y auditada** (y este
documento actualizado con las evidencias) antes de exponer el sistema fuera de
`localhost`, ya sea en LAN, hosting o Internet.

## Remisión

- Informe de auditoría de seguridad emitido por `@security` (rol documentado
  en `agents/Security.md`).
- Hallazgo relacionado en `AGENTS.md`, sección «Seguridad y secretos».
