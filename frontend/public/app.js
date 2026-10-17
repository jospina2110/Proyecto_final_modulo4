const estado = document.getElementById("estado");
const listado = document.getElementById("pacientes");

const MENSAJE_SIN_CONEXION = "No fue posible conectar con la API.";
const MENSAJE_RESPUESTA_INESPERADA = "La API devolvió una respuesta inesperada.";
const MENSAJE_SIN_DETALLE = "La API no proporcionó el detalle del error.";

// El backend responde los errores como {"detail": ...} (ver el middleware
// de excepciones). En los 422 de validación, detail es un arreglo de errores.
function extraerDetalle(cuerpo) {
    if (!cuerpo || typeof cuerpo !== "object") {
        return MENSAJE_SIN_DETALLE;
    }
    if (typeof cuerpo.detail === "string" && cuerpo.detail.trim() !== "") {
        return cuerpo.detail;
    }
    if (Array.isArray(cuerpo.detail)) {
        const mensajes = cuerpo.detail
            .filter((item) => item && typeof item.msg === "string")
            .map((item) => item.msg);
        if (mensajes.length > 0) {
            return mensajes.join("; ");
        }
    }
    return MENSAJE_SIN_DETALLE;
}

async function cargarPacientes() {
    let respuesta;
    try {
        respuesta = await fetch("/api/patients");
    } catch {
        estado.textContent = MENSAJE_SIN_CONEXION;
        return;
    }

    if (!respuesta.ok) {
        let cuerpo = null;
        try {
            cuerpo = await respuesta.json();
        } catch {
            cuerpo = null;
        }
        estado.textContent = `Error ${respuesta.status}: ${extraerDetalle(cuerpo)}`;
        return;
    }

    let pacientes;
    try {
        pacientes = await respuesta.json();
    } catch {
        estado.textContent = MENSAJE_RESPUESTA_INESPERADA;
        return;
    }

    if (!Array.isArray(pacientes)) {
        estado.textContent = MENSAJE_RESPUESTA_INESPERADA;
        return;
    }

    if (pacientes.length === 0) {
        estado.textContent = "No hay pacientes registrados.";
        return;
    }

    estado.textContent = `Pacientes registrados: ${pacientes.length}`;
    pacientes.forEach((paciente) => {
        const item = document.createElement("li");
        item.textContent = `${paciente.full_name} — ${paciente.email}`;
        listado.appendChild(item);
    });
}

cargarPacientes().catch(() => {
    estado.textContent = "Ocurrió un error inesperado al cargar los pacientes.";
});