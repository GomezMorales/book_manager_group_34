"""Repositorios CSV para las entidades de Book Manager."""

import abc
import csv
import os
from datetime import date
from typing import Generic, List, Optional, TypeVar

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

T = TypeVar("T", bound=EntidadBase)


# ---------------------------------------------------------------------------
# Interfaces
# ---------------------------------------------------------------------------

class IRepositorio(abc.ABC, Generic[T]):
    """Interfaz para repositorios que manejan entidades con operaciones CRUD básicas."""

    @abc.abstractmethod
    def crear(self, entidad: T) -> T:
        """Crea una nueva entidad en el repositorio.

        Args:
            entidad (T): La entidad a crear.

        Returns:
            T: La entidad creada.

        Raises:
            ValueError: Si ya existe una entidad con el mismo ID.
        """
        pass

    @abc.abstractmethod
    def leer_por_id(self, id: int) -> Optional[T]:
        """Lee una entidad del repositorio por su ID.

        Args:
            id (int): El ID de la entidad a leer.

        Returns:
            Optional[T]: La entidad si se encuentra, None en caso contrario.
        """
        pass

    @abc.abstractmethod
    def leer_todos(self) -> List[T]:
        """Lee todas las entidades del repositorio.

        Returns:
            List[T]: Una lista de todas las entidades.
        """
        pass

    @abc.abstractmethod
    def actualizar(self, entidad: T) -> T:
        """Actualiza una entidad existente en el repositorio.

        Args:
            entidad (T): La entidad a actualizar (debe tener un ID existente).

        Returns:
            T: La entidad actualizada.

        Raises:
            ValueError: Si no se encuentra la entidad para actualizar.
        """
        pass

    @abc.abstractmethod
    def eliminar(self, id: int) -> bool:
        """Elimina una entidad del repositorio por su ID.

        Args:
            id (int): El ID de la entidad a eliminar.

        Returns:
            bool: True si la entidad fue eliminada, False si no se encontró.
        """
        pass


class IRepositorioStock(abc.ABC):
    """Interfaz para repositorios del tipo Stock."""

    @abc.abstractmethod
    def crear(self, stock: Stock) -> Stock:
        """Crea un nuevo registro de stock.

        Args:
            stock (Stock): El objeto Stock a crear.

        Returns:
            Stock: El objeto Stock creado.

        Raises:
            ValueError: Si ya existe un registro de stock para el mismo libro.
        """
        pass

    @abc.abstractmethod
    def leer_por_libro(self, libro_id: int) -> Optional[Stock]:
        """Lee un registro de stock por ID de libro.

        Args:
            libro_id (int): El ID del libro asociado al stock.

        Returns:
            Optional[Stock]: El objeto Stock si se encuentra, None en caso contrario.
        """
        pass

    @abc.abstractmethod
    def actualizar(self, stock: Stock) -> Stock:
        """Actualiza un registro de stock existente.

        Args:
            stock (Stock): El objeto Stock a actualizar (debe tener un libro_id existente).

        Returns:
            Stock: El objeto Stock actualizado.

        Raises:
            ValueError: Si no se encuentra el stock para actualizar.
        """
        pass

    @abc.abstractmethod
    def eliminar(self, libro_id: int) -> bool:
        """Elimina un registro de stock por ID de libro.

        Args:
            libro_id (int): El ID del libro asociado al stock a eliminar.

        Returns:
            bool: True si el stock fue eliminado, False si no se encontró.
        """
        pass


class IRepositorioCotizacionDolar(abc.ABC):
    """Interfaz para repositorios del tipo CotizacionDolar."""

    @abc.abstractmethod
    def crear(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        """Crea una nueva cotización de dólar.

        Args:
            cotizacion (CotizacionDolar): El objeto CotizacionDolar a crear.

        Returns:
            CotizacionDolar: El objeto CotizacionDolar creado.

        Raises:
            ValueError: Si ya existe una cotización para el mismo tipo y fecha.
        """
        pass

    @abc.abstractmethod
    def leer_por_tipo_y_fecha(self, tipo_id: int, fecha: date) -> Optional[CotizacionDolar]:
        """Lee una cotización de dólar por tipo y fecha.

        Args:
            tipo_id (int): El ID del tipo de cotización.
            fecha (date): La fecha de la cotización.

        Returns:
            Optional[CotizacionDolar]: La cotización si se encuentra, None en caso contrario.
        """
        pass

    @abc.abstractmethod
    def leer_historico_por_tipo(self, tipo_id: int) -> List[CotizacionDolar]:
        """Lee el histórico de cotizaciones para un tipo específico.

        Args:
            tipo_id (int): El ID del tipo de cotización.

        Returns:
            List[CotizacionDolar]: Una lista de cotizaciones históricas para el tipo dado.
        """
        pass

    @abc.abstractmethod
    def actualizar(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        """Actualiza una cotización de dólar existente.

        Args:
            cotizacion (CotizacionDolar): El objeto CotizacionDolar a actualizar.

        Returns:
            CotizacionDolar: El objeto CotizacionDolar actualizado.
        """
        pass

    @abc.abstractmethod
    def eliminar(self, tipo_id: int, fecha: date) -> bool:
        """Elimina una cotización de dólar por tipo y fecha.

        Args:
            tipo_id (int): El ID del tipo de cotización.
            fecha (date): La fecha de la cotización a eliminar.

        Returns:
            bool: True si la cotización fue eliminada, False si no se encontró.
        """
        pass


# ---------------------------------------------------------------------------
# Implementaciones concretas
# ---------------------------------------------------------------------------

class RepositorioGenero(IRepositorio[Genero]):
    """Repositorio CSV para la entidad Genero."""

    def __init__(self, ruta_csv: str) -> None:
        self._ruta = ruta_csv

    def crear(self, entidad: Genero) -> Genero:
        todos = self.leer_todos()
        if any(g.id == entidad.id for g in todos):
            raise ValueError(f"Ya existe un género con id {entidad.id}")
        with open(self._ruta, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([entidad.id, entidad.nombre])
        return entidad

    def leer_todos(self) -> List[Genero]:
        generos: List[Genero] = []
        if not os.path.exists(self._ruta):
            return generos
        with open(self._ruta, newline="", encoding="utf-8") as f:
            for fila in csv.reader(f):
                if fila:
                    generos.append(Genero(int(fila[0]), fila[1]))
        return generos

    def leer_por_id(self, id: int) -> Optional[Genero]:
        return next((g for g in self.leer_todos() if g.id == id), None)

    def actualizar(self, entidad: Genero) -> Genero:
        todos = self.leer_todos()
        if not any(g.id == entidad.id for g in todos):
            raise ValueError(f"No existe un género con id {entidad.id}")
        with open(self._ruta, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for g in todos:
                writer.writerow([entidad.id, entidad.nombre] if g.id == entidad.id else [g.id, g.nombre])
        return entidad

    def eliminar(self, id: int) -> bool:
        todos = self.leer_todos()
        nuevos = [g for g in todos if g.id != id]
        if len(nuevos) == len(todos):
            return False
        with open(self._ruta, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for g in nuevos:
                writer.writerow([g.id, g.nombre])
        return True


class RepositorioEditorial(IRepositorio[Editorial]):
    """Repositorio CSV para la entidad Editorial."""

    def __init__(self, ruta_csv: str) -> None:
        self._ruta = ruta_csv

    def crear(self, entidad: Editorial) -> Editorial:
        todos = self.leer_todos()
        if any(e.id == entidad.id for e in todos):
            raise ValueError(f"Ya existe una editorial con id {entidad.id}")
        with open(self._ruta, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([entidad.id, entidad.nombre])
        return entidad

    def leer_todos(self) -> List[Editorial]:
        editoriales: List[Editorial] = []
        if not os.path.exists(self._ruta):
            return editoriales
        with open(self._ruta, newline="", encoding="utf-8") as f:
            for fila in csv.reader(f):
                if fila:
                    editoriales.append(Editorial(int(fila[0]), fila[1]))
        return editoriales

    def leer_por_id(self, id: int) -> Optional[Editorial]:
        return next((e for e in self.leer_todos() if e.id == id), None)

    def actualizar(self, entidad: Editorial) -> Editorial:
        todos = self.leer_todos()
        if not any(e.id == entidad.id for e in todos):
            raise ValueError(f"No existe una editorial con id {entidad.id}")
        with open(self._ruta, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for e in todos:
                writer.writerow([entidad.id, entidad.nombre] if e.id == entidad.id else [e.id, e.nombre])
        return entidad

    def eliminar(self, id: int) -> bool:
        todos = self.leer_todos()
        nuevos = [e for e in todos if e.id != id]
        if len(nuevos) == len(todos):
            return False
        with open(self._ruta, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for e in nuevos:
                writer.writerow([e.id, e.nombre])
        return True


class RepositorioMoneda(IRepositorio[Moneda]):
    """Repositorio CSV para la entidad Moneda."""

    def __init__(self, ruta_csv: str) -> None:
        self._ruta = ruta_csv

    def crear(self, entidad: Moneda) -> Moneda:
        todos = self.leer_todos()
        if any(m.id == entidad.id for m in todos):
            raise ValueError(f"Ya existe una moneda con id {entidad.id}")
        with open(self._ruta, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([entidad.id, entidad.codigo, entidad.descripcion])
        return entidad

    def leer_todos(self) -> List[Moneda]:
        monedas: List[Moneda] = []
        if not os.path.exists(self._ruta):
            return monedas
        with open(self._ruta, newline="", encoding="utf-8") as f:
            for fila in csv.reader(f):
                if fila:
                    monedas.append(Moneda(int(fila[0]), fila[1], fila[2]))
        return monedas

    def leer_por_id(self, id: int) -> Optional[Moneda]:
        return next((m for m in self.leer_todos() if m.id == id), None)

    def actualizar(self, entidad: Moneda) -> Moneda:
        todos = self.leer_todos()
        if not any(m.id == entidad.id for m in todos):
            raise ValueError(f"No existe una moneda con id {entidad.id}")
        with open(self._ruta, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for m in todos:
                writer.writerow([entidad.id, entidad.codigo, entidad.descripcion] if m.id == entidad.id else [m.id, m.codigo, m.descripcion])
        return entidad

    def eliminar(self, id: int) -> bool:
        todos = self.leer_todos()
        nuevos = [m for m in todos if m.id != id]
        if len(nuevos) == len(todos):
            return False
        with open(self._ruta, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for m in nuevos:
                writer.writerow([m.id, m.codigo, m.descripcion])
        return True


class RepositorioTipoCotizacion(IRepositorio[TipoCotizacion]):
    """Repositorio CSV para la entidad TipoCotizacion."""

    def __init__(self, ruta_csv: str) -> None:
        self._ruta = ruta_csv

    def crear(self, entidad: TipoCotizacion) -> TipoCotizacion:
        todos = self.leer_todos()
        if any(t.id == entidad.id for t in todos):
            raise ValueError(f"Ya existe un tipo de cotización con id {entidad.id}")
        with open(self._ruta, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([entidad.id, entidad.nombre])
        return entidad

    def leer_todos(self) -> List[TipoCotizacion]:
        tipos: List[TipoCotizacion] = []
        if not os.path.exists(self._ruta):
            return tipos
        with open(self._ruta, newline="", encoding="utf-8") as f:
            for fila in csv.reader(f):
                if fila:
                    tipos.append(TipoCotizacion(int(fila[0]), fila[1]))
        return tipos

    def leer_por_id(self, id: int) -> Optional[TipoCotizacion]:
        return next((t for t in self.leer_todos() if t.id == id), None)

    def actualizar(self, entidad: TipoCotizacion) -> TipoCotizacion:
        todos = self.leer_todos()
        if not any(t.id == entidad.id for t in todos):
            raise ValueError(f"No existe un tipo de cotización con id {entidad.id}")
        with open(self._ruta, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for t in todos:
                writer.writerow([entidad.id, entidad.nombre] if t.id == entidad.id else [t.id, t.nombre])
        return entidad

    def eliminar(self, id: int) -> bool:
        todos = self.leer_todos()
        nuevos = [t for t in todos if t.id != id]
        if len(nuevos) == len(todos):
            return False
        with open(self._ruta, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for t in nuevos:
                writer.writerow([t.id, t.nombre])
        return True


class RepositorioLibro(IRepositorio[Libro]):
    """Repositorio CSV para la entidad Libro."""

    def __init__(
        self,
        ruta_csv: str,
        repo_genero: RepositorioGenero,
        repo_editorial: RepositorioEditorial,
    ) -> None:
        self._ruta = ruta_csv
        self._repo_genero = repo_genero
        self._repo_editorial = repo_editorial

    def crear(self, entidad: Libro) -> Libro:
        todos = self.leer_todos()
        if any(l.id == entidad.id for l in todos):
            raise ValueError(f"Ya existe un libro con id {entidad.id}")
        with open(self._ruta, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([
                entidad.id, entidad.isbn, entidad.titulo,
                entidad.autor, entidad.genero.id, entidad.editorial.id,
            ])
        return entidad

    def leer_todos(self) -> List[Libro]:
        libros: List[Libro] = []
        if not os.path.exists(self._ruta):
            return libros
        with open(self._ruta, newline="", encoding="utf-8") as f:
            for fila in csv.reader(f):
                if fila:
                    genero = self._repo_genero.leer_por_id(int(fila[4]))
                    editorial = self._repo_editorial.leer_por_id(int(fila[5]))
                    libros.append(Libro(int(fila[0]), fila[1], fila[2], fila[3], genero, editorial))
        return libros

    def leer_por_id(self, id: int) -> Optional[Libro]:
        return next((l for l in self.leer_todos() if l.id == id), None)

    def actualizar(self, entidad: Libro) -> Libro:
        todos = self.leer_todos()
        if not any(l.id == entidad.id for l in todos):
            raise ValueError(f"No existe un libro con id {entidad.id}")
        with open(self._ruta, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for l in todos:
                if l.id == entidad.id:
                    writer.writerow([entidad.id, entidad.isbn, entidad.titulo, entidad.autor, entidad.genero.id, entidad.editorial.id])
                else:
                    writer.writerow([l.id, l.isbn, l.titulo, l.autor, l.genero.id, l.editorial.id])
        return entidad

    def eliminar(self, id: int) -> bool:
        todos = self.leer_todos()
        nuevos = [l for l in todos if l.id != id]
        if len(nuevos) == len(todos):
            return False
        with open(self._ruta, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for l in nuevos:
                writer.writerow([l.id, l.isbn, l.titulo, l.autor, l.genero.id, l.editorial.id])
        return True


class RepositorioPrecio(IRepositorio[Precio]):
    """Repositorio CSV para la entidad Precio."""

    def __init__(
        self,
        ruta_csv: str,
        repo_libro: RepositorioLibro,
        repo_moneda: RepositorioMoneda,
    ) -> None:
        self._ruta = ruta_csv
        self._repo_libro = repo_libro
        self._repo_moneda = repo_moneda

    def crear(self, entidad: Precio) -> Precio:
        todos = self.leer_todos()
        if any(p.id == entidad.id for p in todos):
            raise ValueError(f"Ya existe un precio con id {entidad.id}")
        with open(self._ruta, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([
                entidad.id, entidad.libro.id, entidad.monto, entidad.moneda.id,
            ])
        return entidad

    def leer_todos(self) -> List[Precio]:
        precios: List[Precio] = []
        if not os.path.exists(self._ruta):
            return precios
        with open(self._ruta, newline="", encoding="utf-8") as f:
            for fila in csv.reader(f):
                if fila:
                    libro = self._repo_libro.leer_por_id(int(fila[1]))
                    moneda = self._repo_moneda.leer_por_id(int(fila[3]))
                    precios.append(Precio(int(fila[0]), libro, float(fila[2]), moneda))
        return precios

    def leer_por_id(self, id: int) -> Optional[Precio]:
        return next((p for p in self.leer_todos() if p.id == id), None)

    def actualizar(self, entidad: Precio) -> Precio:
        todos = self.leer_todos()
        if not any(p.id == entidad.id for p in todos):
            raise ValueError(f"No existe un precio con id {entidad.id}")
        with open(self._ruta, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for p in todos:
                if p.id == entidad.id:
                    writer.writerow([entidad.id, entidad.libro.id, entidad.monto, entidad.moneda.id])
                else:
                    writer.writerow([p.id, p.libro.id, p.monto, p.moneda.id])
        return entidad

    def eliminar(self, id: int) -> bool:
        todos = self.leer_todos()
        nuevos = [p for p in todos if p.id != id]
        if len(nuevos) == len(todos):
            return False
        with open(self._ruta, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for p in nuevos:
                writer.writerow([p.id, p.libro.id, p.monto, p.moneda.id])
        return True


class RepositorioStock(IRepositorioStock):
    """Repositorio CSV para la entidad Stock."""

    def __init__(self, ruta_csv: str, repo_libro: RepositorioLibro) -> None:
        self._ruta = ruta_csv
        self._repo_libro = repo_libro

    def crear(self, stock: Stock) -> Stock:
        if self.leer_por_libro(stock.libro.id) is not None:
            raise ValueError(f"Ya existe stock para el libro con id {stock.libro.id}")
        with open(self._ruta, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([stock.libro.id, stock.cantidad])
        return stock

    def leer_por_libro(self, libro_id: int) -> Optional[Stock]:
        if not os.path.exists(self._ruta):
            return None
        with open(self._ruta, newline="", encoding="utf-8") as f:
            for fila in csv.reader(f):
                if fila and int(fila[0]) == libro_id:
                    libro = self._repo_libro.leer_por_id(libro_id)
                    return Stock(libro, int(fila[1]))
        return None

    def _leer_todas_las_filas(self) -> List[List[str]]:
        if not os.path.exists(self._ruta):
            return []
        with open(self._ruta, newline="", encoding="utf-8") as f:
            return [fila for fila in csv.reader(f) if fila]

    def actualizar(self, stock: Stock) -> Stock:
        filas = self._leer_todas_las_filas()
        if not any(int(f[0]) == stock.libro.id for f in filas):
            raise ValueError(f"No existe stock para el libro con id {stock.libro.id}")
        with open(self._ruta, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for fila in filas:
                writer.writerow([stock.libro.id, stock.cantidad] if int(fila[0]) == stock.libro.id else fila)
        return stock

    def eliminar(self, libro_id: int) -> bool:
        filas = self._leer_todas_las_filas()
        nuevas = [f for f in filas if int(f[0]) != libro_id]
        if len(nuevas) == len(filas):
            return False
        with open(self._ruta, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for fila in nuevas:
                writer.writerow(fila)
        return True


class RepositorioCotizacionDolar(IRepositorioCotizacionDolar):
    """Repositorio CSV para la entidad CotizacionDolar."""

    def __init__(self, ruta_csv: str, repo_tipo: RepositorioTipoCotizacion) -> None:
        self._ruta = ruta_csv
        self._repo_tipo = repo_tipo

    def _leer_todas_las_filas(self) -> List[List[str]]:
        if not os.path.exists(self._ruta):
            return []
        with open(self._ruta, newline="", encoding="utf-8") as f:
            return [fila for fila in csv.reader(f) if fila]

    def _fila_a_cotizacion(self, fila: List[str]) -> CotizacionDolar:
        tipo = self._repo_tipo.leer_por_id(int(fila[0]))
        return CotizacionDolar(tipo, date.fromisoformat(fila[1]), float(fila[2]))

    def crear(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        if self.leer_por_tipo_y_fecha(cotizacion.tipo_cotizacion.id, cotizacion.fecha) is not None:
            raise ValueError("Ya existe una cotización para ese tipo y fecha.")
        with open(self._ruta, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([
                cotizacion.tipo_cotizacion.id,
                cotizacion.fecha.isoformat(),
                cotizacion.valor,
            ])
        return cotizacion

    def leer_por_tipo_y_fecha(self, tipo_id: int, fecha: date) -> Optional[CotizacionDolar]:
        for fila in self._leer_todas_las_filas():
            if int(fila[0]) == tipo_id and fila[1] == fecha.isoformat():
                return self._fila_a_cotizacion(fila)
        return None

    def leer_historico_por_tipo(self, tipo_id: int) -> List[CotizacionDolar]:
        return [
            self._fila_a_cotizacion(f)
            for f in self._leer_todas_las_filas()
            if int(f[0]) == tipo_id
        ]

    def actualizar(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        filas = self._leer_todas_las_filas()
        tipo_id = cotizacion.tipo_cotizacion.id
        fecha_iso = cotizacion.fecha.isoformat()
        if not any(int(f[0]) == tipo_id and f[1] == fecha_iso for f in filas):
            raise ValueError("No existe la cotización para actualizar.")
        with open(self._ruta, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for fila in filas:
                if int(fila[0]) == tipo_id and fila[1] == fecha_iso:
                    writer.writerow([tipo_id, fecha_iso, cotizacion.valor])
                else:
                    writer.writerow(fila)
        return cotizacion

    def eliminar(self, tipo_id: int, fecha: date) -> bool:
        filas = self._leer_todas_las_filas()
        fecha_iso = fecha.isoformat()
        nuevas = [f for f in filas if not (int(f[0]) == tipo_id and f[1] == fecha_iso)]
        if len(nuevas) == len(filas):
            return False
        with open(self._ruta, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for fila in nuevas:
                writer.writerow(fila)
        return True
