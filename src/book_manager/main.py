"""Punto de entrada de Book Manager."""

from pathlib import Path

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
from book_manager.ui.console import ConsolaBookManager


RUTA_CSV = Path(__file__).resolve().parent / "migrations" / "csv"


def main(import_default_data: bool = False) -> None:
	"""Configura persistencia y servicios e inicia la interfaz de consola.

	Args:
		import_default_data: Si es True, reemplaza los CSV por los datos de ejemplo.
	"""
	RUTA_CSV.mkdir(parents=True, exist_ok=True)
	if import_default_data:
		cargar_datos_iniciales(RUTA_CSV)

	repo_genero = RepositorioGenero(str(RUTA_CSV / "generos.csv"))
	repo_editorial = RepositorioEditorial(str(RUTA_CSV / "editoriales.csv"))
	repo_moneda = RepositorioMoneda(str(RUTA_CSV / "monedas.csv"))
	repo_tipo = RepositorioTipoCotizacion(str(RUTA_CSV / "tipos_cotizacion.csv"))
	repo_libro = RepositorioLibro(
		str(RUTA_CSV / "libros.csv"), repo_genero, repo_editorial
	)
	repo_precio = RepositorioPrecio(
		str(RUTA_CSV / "precios.csv"), repo_libro, repo_moneda
	)
	repo_stock = RepositorioStock(str(RUTA_CSV / "stock.csv"), repo_libro)
	repo_cotizacion = RepositorioCotizacionDolar(
		str(RUTA_CSV / "cotizaciones_dolar.csv"), repo_tipo
	)

	servicio_genero = ServicioGenero(repo_genero, repo_libro)
	servicio_editorial = ServicioEditorial(repo_editorial, repo_libro)
	servicio_moneda = ServicioMoneda(repo_moneda, repo_precio)
	servicio_tipo = ServicioTipoCotizacion(repo_tipo, repo_cotizacion)
	servicio_libro = ServicioLibro(
		repo_libro, repo_genero, repo_editorial, repo_precio, repo_stock
	)
	servicio_precio = ServicioPrecio(repo_precio, repo_libro, repo_moneda)
	servicio_stock = ServicioStock(repo_stock, repo_libro)
	servicio_cotizacion = ServicioCotizacionDolar(repo_cotizacion, repo_tipo)

	consola = ConsolaBookManager(
		servicio_libro,
		servicio_genero,
		servicio_editorial,
		servicio_moneda,
		servicio_tipo,
		servicio_precio,
		servicio_stock,
		servicio_cotizacion,
	)
	consola.ejecutar()


if __name__ == "__main__":
	main()
