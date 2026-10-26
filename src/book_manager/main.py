"""Punto de entrada de Book Manager."""

from book_manager.database.connection import ConexionDB
from book_manager.models.models import Auditoria
from book_manager.preload_data.preload_data import cargar_datos_iniciales
from book_manager.repositories.repositories import (
    RepositorioCotizacionDolar,
    RepositorioEditorial,
    RepositorioGenero,
    RepositorioLibro,
    RepositorioMoneda,
    RepositorioPrecio,
    RepositorioStock,
    RepositorioTipoCotizacion,
)
from book_manager.services.services import (
    ServicioCotizacionDolar,
    ServicioEditorial,
    ServicioGenero,
    ServicioLibro,
    ServicioMoneda,
    ServicioPrecio,
    ServicioStock,
    ServicioTipoCotizacion,
)
from book_manager.services.alertas import ServicioAlertasPrecio
from book_manager.services.auditoria import ServicioAuditoria
from book_manager.ui.console import ConsolaBookManager


def main(import_default_data: bool = False) -> None:
    """Configura persistencia y servicios e inicia la interfaz de consola.

    Args:
            import_default_data: Si es True, reemplaza los datos de la base
                por los datos de ejemplo.
    """
    conexion = ConexionDB()
    try:
        Auditoria.__table__.create(conexion.engine, checkfirst=True)
        if import_default_data:
            cargar_datos_iniciales(conexion)

        repo_genero = RepositorioGenero(conexion)
        repo_editorial = RepositorioEditorial(conexion)
        repo_moneda = RepositorioMoneda(conexion)
        repo_tipo = RepositorioTipoCotizacion(conexion)
        repo_libro = RepositorioLibro(conexion)
        repo_precio = RepositorioPrecio(conexion)
        repo_stock = RepositorioStock(conexion)
        repo_cotizacion = RepositorioCotizacionDolar(conexion)

        servicio_genero = ServicioGenero(repo_genero, repo_libro)
        servicio_editorial = ServicioEditorial(repo_editorial, repo_libro)
        servicio_moneda = ServicioMoneda(repo_moneda, repo_precio)
        servicio_tipo = ServicioTipoCotizacion(repo_tipo, repo_cotizacion)
        servicio_libro = ServicioLibro(
            repo_libro, repo_genero, repo_editorial, repo_precio, repo_stock
        )
        servicio_precio = ServicioPrecio(repo_precio, repo_libro, repo_moneda)
        servicio_stock = ServicioStock(repo_stock, repo_libro)
        servicio_cotizacion = ServicioCotizacionDolar(
            repo_cotizacion, repo_tipo
        )
        servicio_alertas = ServicioAlertasPrecio(servicio_precio)
        servicio_auditoria = ServicioAuditoria(conexion)

        consola = ConsolaBookManager(
            servicio_libro,
            servicio_genero,
            servicio_editorial,
            servicio_moneda,
            servicio_tipo,
            servicio_precio,
            servicio_stock,
            servicio_cotizacion,
            servicio_alertas,
            servicio_auditoria,
        )
        consola.ejecutar()
    finally:
        conexion.cerrar()


if __name__ == "__main__":
    main()
