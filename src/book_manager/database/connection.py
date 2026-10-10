"""Conexión a la base de datos mediante SQLAlchemy."""

import os
from pathlib import Path
from typing import Optional
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
        """Devuelve una sesión nueva para operar con la base de datos."""
        return Session(self._engine)

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
