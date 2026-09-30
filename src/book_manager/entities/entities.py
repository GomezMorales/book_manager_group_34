"""Entidades del dominio de Book Manager."""

import abc
from datetime import date


class EntidadBase(abc.ABC):
  """Clase base para las entidades identificables por un id entero."""

  def __init__(self, id: int) -> None:
    self._id = id

  @property
  def id(self) -> int:
    return self._id


class Genero(EntidadBase):
  """Categoría literaria a la que pertenece un libro."""

  def __init__(self, id_genero: int, nombre: str) -> None:
    super().__init__(id_genero)
    self._nombre = nombre

  @property
  def nombre(self) -> str:
    return self._nombre

  @nombre.setter
  def nombre(self, value: str) -> None:
    self._nombre = value


class Editorial(EntidadBase):
  """Proveedor/distribuidora que provee los libros a la librería."""

  def __init__(self, id_editorial: int, nombre: str) -> None:
    super().__init__(id_editorial)
    self._nombre = nombre

  @property
  def nombre(self) -> str:
    return self._nombre

  @nombre.setter
  def nombre(self, value: str) -> None:
    self._nombre = value


class Moneda(EntidadBase):
  """Moneda en la que se puede expresar un precio (ARS, USD, etc.)."""

  def __init__(self, id_moneda: int, codigo: str, descripcion: str) -> None:
    super().__init__(id_moneda)
    self._codigo = codigo
    self._descripcion = descripcion

  @property
  def codigo(self) -> str:
    return self._codigo

  @codigo.setter
  def codigo(self, value: str) -> None:
    self._codigo = value

  @property
  def descripcion(self) -> str:
    return self._descripcion

  @descripcion.setter
  def descripcion(self, value: str) -> None:
    self._descripcion = value


class TipoCotizacion(EntidadBase):
  """Tipo de cotización del dólar (Oficial, Blue, MEP, etc.)."""

  def __init__(self, id_tipo: int, nombre: str) -> None:
    super().__init__(id_tipo)
    self._nombre = nombre

  @property
  def nombre(self) -> str:
    return self._nombre

  @nombre.setter
  def nombre(self, value: str) -> None:
    self._nombre = value


class Libro(EntidadBase):
  """Título del catálogo de la librería."""

  def __init__(
      self,
      id_libro: int,
      isbn: str,
      titulo: str,
      autor: str,
      genero: Genero,
      editorial: Editorial,
  ) -> None:
    super().__init__(id_libro)
    self._isbn = isbn
    self._titulo = titulo
    self._autor = autor
    self._genero = genero
    self._editorial = editorial

  @property
  def isbn(self) -> str:
    return self._isbn

  @isbn.setter
  def isbn(self, value: str) -> None:
    self._isbn = value

  @property
  def titulo(self) -> str:
    return self._titulo

  @titulo.setter
  def titulo(self, value: str) -> None:
    self._titulo = value

  @property
  def autor(self) -> str:
    return self._autor

  @autor.setter
  def autor(self, value: str) -> None:
    self._autor = value

  @property
  def genero(self) -> Genero:
    return self._genero

  @genero.setter
  def genero(self, value: Genero) -> None:
    self._genero = value

  @property
  def editorial(self) -> Editorial:
    return self._editorial

  @editorial.setter
  def editorial(self, value: Editorial) -> None:
    self._editorial = value


class Precio(EntidadBase):
  """Valor monetario asociado a un libro en una moneda determinada."""

  def __init__(self, id_precio: int, libro: Libro, monto: float, moneda: Moneda) -> None:
    super().__init__(id_precio)
    self._libro = libro
    self._monto = monto
    self._moneda = moneda

  @property
  def libro(self) -> Libro:
    return self._libro

  @libro.setter
  def libro(self, value: Libro) -> None:
    self._libro = value

  @property
  def monto(self) -> float:
    return self._monto

  @monto.setter
  def monto(self, value: float) -> None:
    self._monto = value

  @property
  def moneda(self) -> Moneda:
    return self._moneda

  @moneda.setter
  def moneda(self, value: Moneda) -> None:
    self._moneda = value


class Stock:
  """Cantidad disponible de un libro (se identifica por el libro, no tiene id propio)."""

  def __init__(self, libro: Libro, cantidad: int) -> None:
    self._libro = libro
    self._cantidad = cantidad

  @property
  def libro(self) -> Libro:
    return self._libro

  @libro.setter
  def libro(self, value: Libro) -> None:
    self._libro = value

  @property
  def cantidad(self) -> int:
    return self._cantidad

  @cantidad.setter
  def cantidad(self, value: int) -> None:
    self._cantidad = value


class CotizacionDolar:
  """Registro histórico de la cotización de un tipo de dólar en una fecha."""

  def __init__(self, tipo_cotizacion: TipoCotizacion, fecha: date, valor: float) -> None:
    self._tipo_cotizacion = tipo_cotizacion
    self._fecha = fecha
    self._valor = valor

  @property
  def tipo_cotizacion(self) -> TipoCotizacion:
    return self._tipo_cotizacion

  @tipo_cotizacion.setter
  def tipo_cotizacion(self, value: TipoCotizacion) -> None:
    self._tipo_cotizacion = value

  @property
  def fecha(self) -> date:
    return self._fecha

  @fecha.setter
  def fecha(self, value: date) -> None:
    self._fecha = value

  @property
  def valor(self) -> float:
    return self._valor

  @valor.setter
  def valor(self, value: float) -> None:
    self._valor = value
