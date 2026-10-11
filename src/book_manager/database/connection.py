"""Conexión y transacciones a la base de datos mediante SQLAlchemy."""

import os
from pathlib import Path
from types import TracebackType
from typing import Optional, Type
from urllib.parse import quote_plus

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

RAIZ_PROYECTO = Path(__file__).resolve().parents[3]
RUTA_ENV = RAIZ_PROYECTO / ".env"
VARIABLE_URL = "DATABASE_URL"
VARIABLE_PASSWORD = "DATABASE_PASSWORD"
MARCADOR_PASSWORD = "[YOUR-PASSWORD]"


class ConexionDB:
    """Maneja la conexión a la base de datos usando SQLAlchemy."""

    def __init__(self, url: Optional[str] = None, echo: bool = False) -> None:
        """Crea el engine de SQLAlchemy.

        Args:
            url: URL de conexión. Si no se indica, se lee DATABASE_URL
                del archivo .env.
            echo: En True muestra por pantalla las sentencias SQL ejecutadas.

        Raises:
            ValueError: Si falta la URL o la contraseña de la base.
        """
        url_completa = self._resolver_url(url)
        self._engine: Engine = create_engine(url_completa, echo=echo)

    @property
    def url(self) -> str:
        """URL de conexión en uso, con la contraseña oculta."""
        return self._engine.url.render_as_string(hide_password=True)

    @property
    def engine(self) -> Engine:
        """Engine de SQLAlchemy (solo lectura)."""
        return self._engine

    def obtener_sesion(self) -> Session:
        """Devuelve una sesión nueva para operar con la base de datos.

        Con expire_on_commit=False los objetos leídos se pueden seguir
        usando después de confirmar y cerrar la sesión.
        """
        return Session(self._engine, expire_on_commit=False)

    def transaccion(self) -> "Transaccion":
        """Devuelve un context manager para operar dentro de una transacción.

        Ejemplo:
            with conexion.transaccion() as sesion:
                sesion.add(objeto)
        """
        return Transaccion(self)

    def probar_conexion(self) -> bool:
        """Verifica que se pueda conectar a la base de datos.

        Returns:
            True si la conexión funciona, False en caso contrario.
        """
        try:
            with self._engine.connect() as conexion:
                conexion.execute(text("SELECT 1"))
            return True
        except SQLAlchemyError:
            return False

    def cerrar(self) -> None:
        """Libera las conexiones abiertas por el engine."""
        self._engine.dispose()

    @staticmethod
    def _resolver_url(url: Optional[str]) -> str:
        """Obtiene y valida la URL de conexión.

        Si la URL trae el marcador [YOUR-PASSWORD], lo reemplaza por la
        contraseña guardada en la variable de entorno DATABASE_PASSWORD.
        """
        load_dotenv(RUTA_ENV)
        if url is None:
            url = os.getenv(VARIABLE_URL)

        if not url or not url.strip():
            raise ValueError(
                "No se encontró la URL de la base de datos. "
                f"Definir {VARIABLE_URL} en el archivo .env."
            )
        url = url.strip()

        if MARCADOR_PASSWORD in url:
            password = os.getenv(VARIABLE_PASSWORD)
            if not password:
                raise ValueError(
                    "Falta la contraseña de la base de datos. "
                    f"Definir la variable de entorno {VARIABLE_PASSWORD}."
                )
            url = url.replace(MARCADOR_PASSWORD, quote_plus(password))
        return url


class Transaccion:
    """Context manager para manejar las transacciones a la base de datos.

    Al entrar al bloque with abre una sesión. Al salir confirma los cambios
    (commit) si no hubo errores o los deshace (rollback) si los hubo. En
    ambos casos cierra la sesión.
    """

    def __init__(self, conexion: ConexionDB) -> None:
        """Guarda la conexión con la que se abrirá la sesión.

        Raises:
            TypeError: Si no se recibe una instancia de ConexionDB.
        """
        if not isinstance(conexion, ConexionDB):
            raise TypeError("Se esperaba una instancia de ConexionDB.")
        self._conexion: ConexionDB = conexion
        self._sesion: Optional[Session] = None

    def __enter__(self) -> Session:
        """Abre la sesión y la entrega al bloque with."""
        self._sesion = self._conexion.obtener_sesion()
        return self._sesion

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> bool:
        """Confirma o deshace los cambios y cierra la sesión.

        Returns:
            False, para que si hubo una excepción se siga propagando.
        """
        try:
            if exc_type is None:
                self._sesion.commit()
            else:
                self._sesion.rollback()
        finally:
            self._sesion.close()
            self._sesion = None
        return False
