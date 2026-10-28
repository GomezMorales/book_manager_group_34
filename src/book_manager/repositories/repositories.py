"""Repositorios SQLAlchemy para las entidades de Book Manager."""

import abc
from contextlib import contextmanager
from datetime import date
from typing import Generator, Generic, List, Optional, TypeVar

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from book_manager.database.connection import ConexionDB
from book_manager.entities.entities import (
    CotizacionDolar,
    Editorial,
    EntidadBase,
    Genero,
    Libro,
    Moneda,
    Precio,
    Stock,
    TipoCotizacion,
)
from book_manager.models.models import (
    Auditoria as ModeloAuditoria,
    CotizacionDolar as ModeloCotizacionDolar,
    Editorial as ModeloEditorial,
    Genero as ModeloGenero,
    Libro as ModeloLibro,
    Moneda as ModeloMoneda,
    Precio as ModeloPrecio,
    Stock as ModeloStock,
    TipoCotizacion as ModeloTipoCotizacion,
)

T = TypeVar("T", bound=EntidadBase)


class IRepositorio(abc.ABC, Generic[T]):
    """Interfaz para repositorios con operaciones CRUD básicas."""

    @abc.abstractmethod
    def crear(self, entidad: T) -> T:
        """Crea una entidad."""

    @abc.abstractmethod
    def leer_por_id(self, id: int) -> Optional[T]:
        """Busca una entidad por su identificador."""

    @abc.abstractmethod
    def leer_todos(self) -> List[T]:
        """Devuelve todas las entidades."""

    @abc.abstractmethod
    def actualizar(self, entidad: T) -> T:
        """Actualiza una entidad existente."""

    @abc.abstractmethod
    def eliminar(self, id: int) -> bool:
        """Elimina una entidad y devuelve si existía."""


class IRepositorioStock(abc.ABC):
    """Interfaz para repositorios del tipo Stock."""

    @abc.abstractmethod
    def crear(self, stock: Stock) -> Stock:
        """Crea un registro de stock."""

    @abc.abstractmethod
    def leer_por_libro(self, libro_id: int) -> Optional[Stock]:
        """Busca el stock asociado a un libro."""

    @abc.abstractmethod
    def actualizar(self, stock: Stock) -> Stock:
        """Actualiza el stock asociado a un libro."""

    @abc.abstractmethod
    def eliminar(self, libro_id: int) -> bool:
        """Elimina el stock asociado a un libro."""


class IRepositorioCotizacionDolar(abc.ABC):
    """Interfaz para repositorios del tipo CotizacionDolar."""

    @abc.abstractmethod
    def crear(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        """Crea una cotización."""

    @abc.abstractmethod
    def leer_por_tipo_y_fecha(
        self, tipo_id: int, fecha: date
    ) -> Optional[CotizacionDolar]:
        """Busca una cotización por tipo y fecha."""

    @abc.abstractmethod
    def leer_historico_por_tipo(self, tipo_id: int) -> List[CotizacionDolar]:
        """Devuelve el histórico de cotizaciones de un tipo."""

    @abc.abstractmethod
    def actualizar(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        """Actualiza una cotización."""

    @abc.abstractmethod
    def eliminar(self, tipo_id: int, fecha: date) -> bool:
        """Elimina una cotización por su clave compuesta."""


class _RepositorioSQLAlchemy:
    """Operaciones comunes de sesión y traducción de errores de integridad."""

    def __init__(self, conexion: ConexionDB) -> None:
        self._conexion = conexion

    @contextmanager
    def _transaccion(self) -> Generator[Session, None, None]:
        try:
            with self._conexion.transaccion() as sesion:
                yield sesion
        except IntegrityError as error:
            raise ValueError(
                "La operación infringe una restricción de integridad "
                "de la base de datos."
            ) from error


def _a_genero(modelo: ModeloGenero) -> Genero:
    return Genero(modelo.id_genero, modelo.nombre)


def _a_editorial(modelo: ModeloEditorial) -> Editorial:
    return Editorial(modelo.id_editorial, modelo.nombre)


def _a_moneda(modelo: ModeloMoneda) -> Moneda:
    return Moneda(modelo.id_moneda, modelo.codigo, modelo.descripcion)


def _a_tipo(modelo: ModeloTipoCotizacion) -> TipoCotizacion:
    return TipoCotizacion(modelo.id_tipo_cotizacion, modelo.nombre)


def _a_libro(modelo: ModeloLibro) -> Libro:
    return Libro(
        modelo.id_libro,
        modelo.isbn,
        modelo.titulo,
        modelo.autor,
        _a_genero(modelo.genero),
        _a_editorial(modelo.editorial),
    )


def _a_precio(modelo: ModeloPrecio) -> Precio:
    return Precio(
        modelo.id_precio,
        _a_libro(modelo.libro),
        float(modelo.monto),
        _a_moneda(modelo.moneda),
    )


def _a_stock(modelo: ModeloStock) -> Stock:
    return Stock(_a_libro(modelo.libro), modelo.cantidad)


def _a_cotizacion(modelo: ModeloCotizacionDolar) -> CotizacionDolar:
    return CotizacionDolar(
        _a_tipo(modelo.tipo_cotizacion), modelo.fecha, float(modelo.valor)
    )


class RepositorioGenero(_RepositorioSQLAlchemy, IRepositorio[Genero]):
    """Repositorio SQL para la entidad Genero."""

    def crear(self, entidad: Genero) -> Genero:
        with self._transaccion() as sesion:
            if sesion.get(ModeloGenero, entidad.id) is not None:
                raise ValueError(f"Ya existe un género con id {entidad.id}")
            sesion.add(
                ModeloGenero(id_genero=entidad.id, nombre=entidad.nombre)
            )
        return entidad

    def leer_por_id(self, id: int) -> Optional[Genero]:
        with self._conexion.obtener_sesion() as sesion:
            modelo = sesion.get(ModeloGenero, id)
            return _a_genero(modelo) if modelo is not None else None

    def leer_todos(self) -> List[Genero]:
        with self._conexion.obtener_sesion() as sesion:
            modelos = sesion.scalars(
                select(ModeloGenero).order_by(ModeloGenero.id_genero)
            )
            return [_a_genero(modelo) for modelo in modelos]

    def actualizar(self, entidad: Genero) -> Genero:
        with self._transaccion() as sesion:
            modelo = sesion.get(ModeloGenero, entidad.id)
            if modelo is None:
                raise ValueError(f"No existe un género con id {entidad.id}")
            modelo.nombre = entidad.nombre
        return entidad

    def eliminar(self, id: int) -> bool:
        with self._transaccion() as sesion:
            modelo = sesion.get(ModeloGenero, id)
            if modelo is None:
                return False
            sesion.delete(modelo)
        return True


class RepositorioEditorial(_RepositorioSQLAlchemy, IRepositorio[Editorial]):
    """Repositorio SQL para la entidad Editorial."""

    def crear(self, entidad: Editorial) -> Editorial:
        with self._transaccion() as sesion:
            if sesion.get(ModeloEditorial, entidad.id) is not None:
                raise ValueError(
                    f"Ya existe una editorial con id {entidad.id}"
                )
            sesion.add(
                ModeloEditorial(
                    id_editorial=entidad.id, nombre=entidad.nombre
                )
            )
        return entidad

    def leer_por_id(self, id: int) -> Optional[Editorial]:
        with self._conexion.obtener_sesion() as sesion:
            modelo = sesion.get(ModeloEditorial, id)
            return _a_editorial(modelo) if modelo is not None else None

    def leer_todos(self) -> List[Editorial]:
        with self._conexion.obtener_sesion() as sesion:
            modelos = sesion.scalars(
                select(ModeloEditorial).order_by(ModeloEditorial.id_editorial)
            )
            return [_a_editorial(modelo) for modelo in modelos]

    def actualizar(self, entidad: Editorial) -> Editorial:
        with self._transaccion() as sesion:
            modelo = sesion.get(ModeloEditorial, entidad.id)
            if modelo is None:
                raise ValueError(
                    f"No existe una editorial con id {entidad.id}"
                )
            modelo.nombre = entidad.nombre
        return entidad

    def eliminar(self, id: int) -> bool:
        with self._transaccion() as sesion:
            modelo = sesion.get(ModeloEditorial, id)
            if modelo is None:
                return False
            sesion.delete(modelo)
        return True


class RepositorioMoneda(_RepositorioSQLAlchemy, IRepositorio[Moneda]):
    """Repositorio SQL para la entidad Moneda."""

    def crear(self, entidad: Moneda) -> Moneda:
        with self._transaccion() as sesion:
            if sesion.get(ModeloMoneda, entidad.id) is not None:
                raise ValueError(f"Ya existe una moneda con id {entidad.id}")
            sesion.add(
                ModeloMoneda(
                    id_moneda=entidad.id,
                    codigo=entidad.codigo,
                    descripcion=entidad.descripcion,
                )
            )
        return entidad

    def leer_por_id(self, id: int) -> Optional[Moneda]:
        with self._conexion.obtener_sesion() as sesion:
            modelo = sesion.get(ModeloMoneda, id)
            return _a_moneda(modelo) if modelo is not None else None

    def leer_todos(self) -> List[Moneda]:
        with self._conexion.obtener_sesion() as sesion:
            modelos = sesion.scalars(
                select(ModeloMoneda).order_by(ModeloMoneda.id_moneda)
            )
            return [_a_moneda(modelo) for modelo in modelos]

    def actualizar(self, entidad: Moneda) -> Moneda:
        with self._transaccion() as sesion:
            modelo = sesion.get(ModeloMoneda, entidad.id)
            if modelo is None:
                raise ValueError(f"No existe una moneda con id {entidad.id}")
            modelo.codigo = entidad.codigo
            modelo.descripcion = entidad.descripcion
        return entidad

    def eliminar(self, id: int) -> bool:
        with self._transaccion() as sesion:
            modelo = sesion.get(ModeloMoneda, id)
            if modelo is None:
                return False
            sesion.delete(modelo)
        return True


class RepositorioTipoCotizacion(
    _RepositorioSQLAlchemy, IRepositorio[TipoCotizacion]
):
    """Repositorio SQL para la entidad TipoCotizacion."""

    def crear(self, entidad: TipoCotizacion) -> TipoCotizacion:
        with self._transaccion() as sesion:
            if sesion.get(ModeloTipoCotizacion, entidad.id) is not None:
                raise ValueError(
                    "Ya existe un tipo de cotización con "
                    f"id {entidad.id}"
                )
            sesion.add(
                ModeloTipoCotizacion(
                    id_tipo_cotizacion=entidad.id, nombre=entidad.nombre
                )
            )
        return entidad

    def leer_por_id(self, id: int) -> Optional[TipoCotizacion]:
        with self._conexion.obtener_sesion() as sesion:
            modelo = sesion.get(ModeloTipoCotizacion, id)
            return _a_tipo(modelo) if modelo is not None else None

    def leer_todos(self) -> List[TipoCotizacion]:
        with self._conexion.obtener_sesion() as sesion:
            modelos = sesion.scalars(
                select(ModeloTipoCotizacion).order_by(
                    ModeloTipoCotizacion.id_tipo_cotizacion
                )
            )
            return [_a_tipo(modelo) for modelo in modelos]

    def actualizar(self, entidad: TipoCotizacion) -> TipoCotizacion:
        with self._transaccion() as sesion:
            modelo = sesion.get(ModeloTipoCotizacion, entidad.id)
            if modelo is None:
                raise ValueError(
                    "No existe un tipo de cotización con "
                    f"id {entidad.id}"
                )
            modelo.nombre = entidad.nombre
        return entidad

    def eliminar(self, id: int) -> bool:
        with self._transaccion() as sesion:
            modelo = sesion.get(ModeloTipoCotizacion, id)
            if modelo is None:
                return False
            sesion.delete(modelo)
        return True


class RepositorioLibro(_RepositorioSQLAlchemy, IRepositorio[Libro]):
    """Repositorio SQL para la entidad Libro."""

    def crear(self, entidad: Libro) -> Libro:
        with self._transaccion() as sesion:
            if sesion.get(ModeloLibro, entidad.id) is not None:
                raise ValueError(f"Ya existe un libro con id {entidad.id}")
            sesion.add(
                ModeloLibro(
                    id_libro=entidad.id,
                    isbn=entidad.isbn,
                    titulo=entidad.titulo,
                    autor=entidad.autor,
                    id_genero=entidad.genero.id,
                    id_editorial=entidad.editorial.id,
                )
            )
        return entidad

    def leer_por_id(self, id: int) -> Optional[Libro]:
        with self._conexion.obtener_sesion() as sesion:
            modelo = sesion.scalar(
                select(ModeloLibro)
                .options(
                    joinedload(ModeloLibro.genero),
                    joinedload(ModeloLibro.editorial),
                )
                .where(ModeloLibro.id_libro == id)
            )
            return _a_libro(modelo) if modelo is not None else None

    def leer_todos(self) -> List[Libro]:
        with self._conexion.obtener_sesion() as sesion:
            modelos = sesion.scalars(
                select(ModeloLibro)
                .options(
                    joinedload(ModeloLibro.genero),
                    joinedload(ModeloLibro.editorial),
                )
                .order_by(ModeloLibro.id_libro)
            )
            return [_a_libro(modelo) for modelo in modelos]

    def actualizar(self, entidad: Libro) -> Libro:
        with self._transaccion() as sesion:
            modelo = sesion.get(ModeloLibro, entidad.id)
            if modelo is None:
                raise ValueError(f"No existe un libro con id {entidad.id}")
            modelo.isbn = entidad.isbn
            modelo.titulo = entidad.titulo
            modelo.autor = entidad.autor
            modelo.id_genero = entidad.genero.id
            modelo.id_editorial = entidad.editorial.id
        return entidad

    def eliminar(self, id: int) -> bool:
        with self._transaccion() as sesion:
            modelo = sesion.get(ModeloLibro, id)
            if modelo is None:
                return False
            sesion.delete(modelo)
        return True


class RepositorioPrecio(_RepositorioSQLAlchemy, IRepositorio[Precio]):
    """Repositorio SQL para la entidad Precio."""

    def crear(self, entidad: Precio) -> Precio:
        with self._transaccion() as sesion:
            if sesion.get(ModeloPrecio, entidad.id) is not None:
                raise ValueError(f"Ya existe un precio con id {entidad.id}")
            sesion.add(
                ModeloPrecio(
                    id_precio=entidad.id,
                    id_libro=entidad.libro.id,
                    monto=entidad.monto,
                    id_moneda=entidad.moneda.id,
                )
            )
        return entidad

    def leer_por_id(self, id: int) -> Optional[Precio]:
        with self._conexion.obtener_sesion() as sesion:
            modelo = sesion.scalar(
                select(ModeloPrecio)
                .options(
                    joinedload(ModeloPrecio.libro).joinedload(
                        ModeloLibro.genero
                    ),
                    joinedload(ModeloPrecio.libro).joinedload(
                        ModeloLibro.editorial
                    ),
                    joinedload(ModeloPrecio.moneda),
                )
                .where(ModeloPrecio.id_precio == id)
            )
            return _a_precio(modelo) if modelo is not None else None

    def leer_todos(self) -> List[Precio]:
        with self._conexion.obtener_sesion() as sesion:
            modelos = sesion.scalars(
                select(ModeloPrecio)
                .options(
                    joinedload(ModeloPrecio.libro).joinedload(
                        ModeloLibro.genero
                    ),
                    joinedload(ModeloPrecio.libro).joinedload(
                        ModeloLibro.editorial
                    ),
                    joinedload(ModeloPrecio.moneda),
                )
                .order_by(ModeloPrecio.id_precio)
            )
            return [_a_precio(modelo) for modelo in modelos]

    def actualizar(self, entidad: Precio) -> Precio:
        with self._transaccion() as sesion:
            modelo = sesion.get(ModeloPrecio, entidad.id)
            if modelo is None:
                raise ValueError(f"No existe un precio con id {entidad.id}")
            modelo.id_libro = entidad.libro.id
            modelo.monto = entidad.monto
            modelo.id_moneda = entidad.moneda.id
        return entidad

    def eliminar(self, id: int) -> bool:
        with self._transaccion() as sesion:
            modelo = sesion.get(ModeloPrecio, id)
            if modelo is None:
                return False
            sesion.delete(modelo)
        return True


class RepositorioStock(_RepositorioSQLAlchemy, IRepositorioStock):
    """Repositorio SQL para la entidad Stock."""

    def crear(self, stock: Stock) -> Stock:
        with self._transaccion() as sesion:
            if sesion.get(ModeloStock, stock.libro.id) is not None:
                raise ValueError(
                    f"Ya existe stock para el libro con id {stock.libro.id}"
                )
            sesion.add(
                ModeloStock(
                    id_libro=stock.libro.id, cantidad=stock.cantidad
                )
            )
        return stock

    def leer_por_libro(self, libro_id: int) -> Optional[Stock]:
        with self._conexion.obtener_sesion() as sesion:
            modelo = sesion.scalar(
                select(ModeloStock)
                .options(
                    joinedload(ModeloStock.libro).joinedload(
                        ModeloLibro.genero
                    ),
                    joinedload(ModeloStock.libro).joinedload(
                        ModeloLibro.editorial
                    ),
                )
                .where(ModeloStock.id_libro == libro_id)
            )
            return _a_stock(modelo) if modelo is not None else None

    def actualizar(self, stock: Stock) -> Stock:
        with self._transaccion() as sesion:
            modelo = sesion.get(ModeloStock, stock.libro.id)
            if modelo is None:
                raise ValueError(
                    f"No existe stock para el libro con id {stock.libro.id}"
                )
            modelo.cantidad = stock.cantidad
        return stock

    def eliminar(self, libro_id: int) -> bool:
        with self._transaccion() as sesion:
            modelo = sesion.get(ModeloStock, libro_id)
            if modelo is None:
                return False
            sesion.delete(modelo)
        return True


class RepositorioCotizacionDolar(
    _RepositorioSQLAlchemy, IRepositorioCotizacionDolar
):
    """Repositorio SQL para la entidad CotizacionDolar."""

    def crear(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        with self._transaccion() as sesion:
            clave = (cotizacion.tipo_cotizacion.id, cotizacion.fecha)
            if sesion.get(ModeloCotizacionDolar, clave) is not None:
                raise ValueError(
                    "Ya existe una cotización para ese tipo y fecha."
                )
            sesion.add(
                ModeloCotizacionDolar(
                    id_tipo_cotizacion=cotizacion.tipo_cotizacion.id,
                    fecha=cotizacion.fecha,
                    valor=cotizacion.valor,
                )
            )
        return cotizacion

    def leer_por_tipo_y_fecha(
        self, tipo_id: int, fecha: date
    ) -> Optional[CotizacionDolar]:
        with self._conexion.obtener_sesion() as sesion:
            modelo = sesion.scalar(
                select(ModeloCotizacionDolar)
                .options(joinedload(ModeloCotizacionDolar.tipo_cotizacion))
                .where(
                    ModeloCotizacionDolar.id_tipo_cotizacion == tipo_id,
                    ModeloCotizacionDolar.fecha == fecha,
                )
            )
            return _a_cotizacion(modelo) if modelo is not None else None

    def leer_historico_por_tipo(self, tipo_id: int) -> List[CotizacionDolar]:
        with self._conexion.obtener_sesion() as sesion:
            modelos = sesion.scalars(
                select(ModeloCotizacionDolar)
                .options(joinedload(ModeloCotizacionDolar.tipo_cotizacion))
                .where(ModeloCotizacionDolar.id_tipo_cotizacion == tipo_id)
                .order_by(ModeloCotizacionDolar.fecha)
            )
            return [_a_cotizacion(modelo) for modelo in modelos]

    def actualizar(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        with self._transaccion() as sesion:
            clave = (cotizacion.tipo_cotizacion.id, cotizacion.fecha)
            modelo = sesion.get(ModeloCotizacionDolar, clave)
            if modelo is None:
                raise ValueError(
                    "No existe una cotización para ese tipo y fecha."
                )
            modelo.valor = cotizacion.valor
        return cotizacion

    def eliminar(self, tipo_id: int, fecha: date) -> bool:
        with self._transaccion() as sesion:
            modelo = sesion.get(ModeloCotizacionDolar, (tipo_id, fecha))
            if modelo is None:
                return False
            sesion.delete(modelo)
        return True


class RepositorioAuditoria(_RepositorioSQLAlchemy):
    """Persiste y consulta los registros de auditoría."""

    def agregar(self, registro: ModeloAuditoria) -> ModeloAuditoria:
        """Guarda un registro de auditoría."""
        with self._transaccion() as sesion:
            sesion.add(registro)
        return registro

    def listar(self) -> List[ModeloAuditoria]:
        """Devuelve los registros, del más reciente al más antiguo."""
        with self._conexion.obtener_sesion() as sesion:
            consulta = select(ModeloAuditoria).order_by(
                ModeloAuditoria.fecha.desc(),
                ModeloAuditoria.id_auditoria.desc(),
            )
            return list(sesion.scalars(consulta))
