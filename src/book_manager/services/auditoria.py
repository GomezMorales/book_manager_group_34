"""Auditoría de las operaciones de negocio de Book Manager."""

import json
from contextvars import ContextVar
from datetime import datetime, timezone
from functools import wraps
from typing import Callable, TypeVar, cast

from book_manager.database.connection import ConexionDB
from book_manager.models.models import Auditoria
from book_manager.repositories.repositories import RepositorioAuditoria

F = TypeVar("F", bound=Callable[..., object])
_OPERACION_AUDITADA: ContextVar[bool] = ContextVar(
    "operacion_auditada", default=False
)


def _obtener_conexion(instancia: object) -> ConexionDB:
    """Obtiene la conexión de la instancia o del servicio que utiliza."""
    conexion = getattr(instancia, "_conexion", None)
    if isinstance(conexion, ConexionDB):
        return conexion

    repositorio = getattr(instancia, "_repo", None)
    conexion = getattr(repositorio, "_conexion", None)
    if isinstance(conexion, ConexionDB):
        return conexion

    servicio_precio = getattr(instancia, "_servicio_precio", None)
    repositorio = getattr(servicio_precio, "_repo", None)
    conexion = getattr(repositorio, "_conexion", None)
    if isinstance(conexion, ConexionDB):
        return conexion

    raise RuntimeError(
        "No se pudo determinar la conexión necesaria para registrar "
        "la auditoría."
    )


def _registrar(
    instancia: object, accion: str, detalles: dict[str, object]
) -> None:
    conexion = _obtener_conexion(instancia)
    registro = Auditoria(
        accion=accion,
        fecha=datetime.now(timezone.utc),
        detalles=json.dumps(detalles, ensure_ascii=False, default=str),
    )
    RepositorioAuditoria(conexion).agregar(registro)


def auditar(funcion: F) -> F:
    """Registra el resultado o el error de una operación pública."""
    accion = funcion.__qualname__

    @wraps(funcion)
    def envoltura(
        instancia: object, *args: object, **kwargs: object
    ) -> object:
        if _OPERACION_AUDITADA.get():
            return funcion(instancia, *args, **kwargs)

        token = _OPERACION_AUDITADA.set(True)
        detalles: dict[str, object] = {
            "argumentos": args,
            "parametros": kwargs,
        }
        try:
            try:
                resultado = funcion(instancia, *args, **kwargs)
            except Exception as error:
                detalles["resultado"] = "error"
                detalles["error"] = f"{type(error).__name__}: {error}"
                try:
                    _registrar(instancia, accion, detalles)
                except Exception as error_auditoria:
                    raise RuntimeError(
                        f"La operación {accion} falló ({error}) y tampoco "
                        f"pudo registrarse en auditoría: {error_auditoria}"
                    ) from error_auditoria
                raise

            detalles["resultado"] = "correcto"
            try:
                _registrar(instancia, accion, detalles)
            except Exception as error_auditoria:
                raise RuntimeError(
                    f"La operación {accion} se ejecutó, pero no pudo "
                    f"registrarse en auditoría: {error_auditoria}"
                ) from error_auditoria
            return resultado
        finally:
            _OPERACION_AUDITADA.reset(token)

    return cast(F, envoltura)


def auditar_metodos_publicos(clase: type[object]) -> type[object]:
    """Aplica auditoría automáticamente a los métodos públicos de servicio."""
    for nombre, atributo in vars(clase).items():
        if isinstance(atributo, (staticmethod, classmethod)):
            continue
        if nombre.startswith("_") or not callable(atributo):
            continue
        setattr(clase, nombre, auditar(atributo))
    return clase


@auditar_metodos_publicos
class ServicioAuditoria:
    """Consulta el historial de auditoría."""

    def __init__(self, conexion: ConexionDB) -> None:
        self._conexion = conexion
        self._repo = RepositorioAuditoria(conexion)

    def listar(self) -> list[Auditoria]:
        """Devuelve los registros más recientes primero."""
        return self._repo.listar()
