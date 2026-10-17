class ResourceNotFoundError(Exception):
    def __init__(self, resource: str, identifier: str) -> None:
        self.resource = resource
        self.identifier = identifier
        super().__init__(f"{resource} no encontrado con identificador {identifier}")


class AppointmentConflictError(Exception):
    def __init__(self, message: str = "El médico ya tiene una cita programada en ese horario") -> None:
        super().__init__(message)


class InvalidStatusTransitionError(Exception):
    def __init__(self, current: str, target: str) -> None:
        self.current = current
        self.target = target
        super().__init__(f"No se permite cambiar el estado de la cita de '{current}' a '{target}'")


class DuplicatePatientError(Exception):
    def __init__(self, message: str = "Ya existe un paciente registrado con los mismos datos") -> None:
        super().__init__(message)