
"""Modelos ORM y esquema relacional de Book Manager."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base declarativa compartida por los modelos ORM."""


class Auditoria(Base):
    """Registro de las operaciones ejecutadas en el sistema."""

    __tablename__ = "auditoria"

    id_auditoria: Mapped[int] = mapped_column(Integer, primary_key=True)
    accion: Mapped[str] = mapped_column(String(150), nullable=False)
    fecha: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    detalles: Mapped[str] = mapped_column(Text, nullable=False)


class Genero(Base):
    """Género literario al que pertenece un libro."""

    __tablename__ = "generos"
    __table_args__ = (UniqueConstraint("nombre", name="uq_generos_nombre"),)

    id_genero: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)

    libros: Mapped[list[Libro]] = relationship(back_populates="genero")


class Editorial(Base):
    """Editorial que publica los libros."""

    __tablename__ = "editoriales"
    __table_args__ = (
        UniqueConstraint("nombre", name="uq_editoriales_nombre"),
    )

    id_editorial: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)

    libros: Mapped[list[Libro]] = relationship(back_populates="editorial")


class Moneda(Base):
    """Moneda en la que se expresa un precio."""

    __tablename__ = "monedas"
    __table_args__ = (
        UniqueConstraint("codigo", name="uq_monedas_codigo"),
    )

    id_moneda: Mapped[int] = mapped_column(Integer, primary_key=True)
    codigo: Mapped[str] = mapped_column(String(3), nullable=False)
    descripcion: Mapped[str] = mapped_column(String(100), nullable=False)

    precios: Mapped[list[Precio]] = relationship(back_populates="moneda")


class TipoCotizacion(Base):
    """Tipo de cotización del dólar."""

    __tablename__ = "tipos_cotizacion"
    __table_args__ = (
        UniqueConstraint("nombre", name="uq_tipos_cotizacion_nombre"),
    )

    id_tipo_cotizacion: Mapped[int] = mapped_column(
        Integer, primary_key=True
    )
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)

    cotizaciones: Mapped[list[CotizacionDolar]] = relationship(
        back_populates="tipo_cotizacion"
    )


class Libro(Base):
    """Libro del catálogo."""

    __tablename__ = "libros"
    __table_args__ = (
        UniqueConstraint("isbn", name="uq_libros_isbn"),
    )

    id_libro: Mapped[int] = mapped_column(Integer, primary_key=True)
    isbn: Mapped[str] = mapped_column(String(13), nullable=False)
    titulo: Mapped[str] = mapped_column(String(255), nullable=False)
    autor: Mapped[str] = mapped_column(String(255), nullable=False)
    id_genero: Mapped[int] = mapped_column(
        ForeignKey("generos.id_genero"), nullable=False
    )
    id_editorial: Mapped[int] = mapped_column(
        ForeignKey("editoriales.id_editorial"), nullable=False
    )

    genero: Mapped[Genero] = relationship(back_populates="libros")
    editorial: Mapped[Editorial] = relationship(back_populates="libros")
    precios: Mapped[list[Precio]] = relationship(back_populates="libro")
    stock: Mapped[Stock | None] = relationship(back_populates="libro")


class Precio(Base):
    """Precio de un libro en una moneda."""

    __tablename__ = "precios"
    __table_args__ = (
        UniqueConstraint(
            "id_libro", "id_moneda", name="uq_precios_libro_moneda"
        ),
        CheckConstraint("monto > 0", name="ck_precios_monto_positivo"),
    )

    id_precio: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_libro: Mapped[int] = mapped_column(
        ForeignKey("libros.id_libro"), nullable=False
    )
    monto: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    id_moneda: Mapped[int] = mapped_column(
        ForeignKey("monedas.id_moneda"), nullable=False
    )

    libro: Mapped[Libro] = relationship(back_populates="precios")
    moneda: Mapped[Moneda] = relationship(back_populates="precios")


class Stock(Base):
    """Existencia de un libro, identificada por su clave foránea."""

    __tablename__ = "stock"
    __table_args__ = (
        CheckConstraint("cantidad >= 0", name="ck_stock_cantidad_no_negativa"),
    )

    id_libro: Mapped[int] = mapped_column(
        ForeignKey("libros.id_libro"), primary_key=True
    )
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)

    libro: Mapped[Libro] = relationship(back_populates="stock")


class CotizacionDolar(Base):
    """Cotización histórica identificada por tipo y fecha."""

    __tablename__ = "cotizaciones_dolar"
    __table_args__ = (
        CheckConstraint("valor > 0", name="ck_cotizaciones_valor_positivo"),
    )

    id_tipo_cotizacion: Mapped[int] = mapped_column(
        ForeignKey("tipos_cotizacion.id_tipo_cotizacion"), primary_key=True
    )
    fecha: Mapped[date] = mapped_column(Date, primary_key=True)
    valor: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)

    tipo_cotizacion: Mapped[TipoCotizacion] = relationship(
        back_populates="cotizaciones"
    )
