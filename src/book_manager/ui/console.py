"""Interfaz de consola para la gestión de la librería."""

import csv
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Callable, List, Sequence

from sqlalchemy.exc import SQLAlchemyError

from book_manager.entities.entities import (
    CotizacionDolar,
    Editorial,
    Genero,
    Libro,
    Moneda,
    Precio,
    Stock,
    TipoCotizacion,
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


@dataclass
class GestorCRUD:
    """Agrupa las operaciones y la presentación de una entidad."""

    nombre: str
    listar: Callable[[], Sequence[object]]
    crear: Callable[[], object]
    actualizar: Callable[[], object]
    eliminar: Callable[[int], object]
    clave: str
    formatear: Callable[[object], str]


class ConsolaBookManager:
    """Presenta los menús y delega las operaciones en los servicios."""

    def __init__(
        self,
        servicio_libro: ServicioLibro,
        servicio_genero: ServicioGenero,
        servicio_editorial: ServicioEditorial,
        servicio_moneda: ServicioMoneda,
        servicio_tipo_cotizacion: ServicioTipoCotizacion,
        servicio_precio: ServicioPrecio,
        servicio_stock: ServicioStock,
        servicio_cotizacion: ServicioCotizacionDolar,
    ) -> None:
        self._libros = servicio_libro
        self._generos = servicio_genero
        self._editoriales = servicio_editorial
        self._monedas = servicio_moneda
        self._tipos = servicio_tipo_cotizacion
        self._precios = servicio_precio
        self._stock = servicio_stock
        self._cotizaciones = servicio_cotizacion
        self._gestores = self._crear_gestores()

    def _crear_gestores(self) -> List[GestorCRUD]:
        return [
            GestorCRUD(
                "Libros",
                self._libros.listar,
                self._crear_libro,
                self._actualizar_libro,
                self._libros.eliminar,
                "id",
                self._formatear,
            ),
            GestorCRUD(
                "Géneros",
                self._generos.listar,
                self._crear_genero,
                self._actualizar_genero,
                self._generos.eliminar,
                "id",
                self._formatear,
            ),
            GestorCRUD(
                "Editoriales",
                self._editoriales.listar,
                self._crear_editorial,
                self._actualizar_editorial,
                self._editoriales.eliminar,
                "id",
                self._formatear,
            ),
            GestorCRUD(
                "Monedas",
                self._monedas.listar,
                self._crear_moneda,
                self._actualizar_moneda,
                self._monedas.eliminar,
                "id",
                self._formatear,
            ),
            GestorCRUD(
                "Tipos de cotización",
                self._tipos.listar,
                self._crear_tipo,
                self._actualizar_tipo,
                self._tipos.eliminar,
                "id",
                self._formatear,
            ),
            GestorCRUD(
                "Precios",
                self._precios.listar,
                self._crear_precio,
                self._actualizar_precio,
                self._precios.eliminar,
                "id",
                self._formatear,
            ),
            GestorCRUD(
                "Stock",
                self._stock.listar,
                self._crear_stock,
                self._actualizar_stock,
                self._eliminar_stock,
                "ID de libro",
                self._formatear,
            ),
            GestorCRUD(
                "Cotizaciones",
                self._cotizaciones.listar,
                self._crear_cotizacion,
                self._actualizar_cotizacion,
                self._eliminar_cotizacion,
                "ID del tipo",
                self._formatear,
            ),
        ]

    def ejecutar(self) -> None:
        """Inicia el menú principal hasta que el usuario elija salir."""
        print("\n=== Book Manager ===")
        while True:
            try:
                self._mostrar_menu_principal()
                opcion = input("Opción: ").strip()
                if opcion == "0":
                    print("Hasta luego.")
                    return
                if opcion in (str(index) for index in range(1, 9)):
                    self._menu_crud(self._gestores[int(opcion) - 1])
                elif opcion == "9":
                    self._menu_stock()
                elif opcion == "10":
                    self._menu_reportes()
                elif opcion == "11":
                    self._obtener_cotizaciones_api()
                else:
                    print("Opción no válida.")
            except (KeyboardInterrupt, EOFError):
                print("\nOperación cancelada. Hasta luego.")
                return
            except (ValueError, OSError, SQLAlchemyError) as error:
                print(f"Error: {error}")

    @staticmethod
    def _mostrar_menu_principal() -> None:
        print(
            "\n1. Libros       2. Géneros       3. Editoriales\n"
            "4. Monedas      5. Tipos dólar   6. Precios\n"
            "7. Stock        8. Cotizaciones  9. Movimientos de stock\n"
            "10. Reportes    11. Obtener cotizaciones por API    0. Salir"
        )

    def _menu_crud(self, gestor: GestorCRUD) -> None:
        while True:
            print(f"\n--- {gestor.nombre} ---")
            print("1. Listar  2. Crear  3. Modificar  4. Eliminar  0. Volver")
            opcion = input("Opción: ").strip()
            try:
                if opcion == "0":
                    return
                if opcion == "1":
                    self._imprimir_lista(gestor.listar(), gestor.formatear)
                elif opcion == "2":
                    gestor.crear()
                    print("Registro creado correctamente.")
                elif opcion == "3":
                    gestor.actualizar()
                    print("Registro actualizado correctamente.")
                elif opcion == "4":
                    identificador = self._leer_entero(
                        f"{gestor.clave.capitalize()} a eliminar: "
                    )
                    if (
                        input("¿Confirmar eliminación? (s/n): ")
                        .strip()
                        .lower()
                        == "s"
                    ):
                        gestor.eliminar(identificador)
                        print("Registro eliminado correctamente.")
                else:
                    print("Opción no válida.")
            except (ValueError, OSError, SQLAlchemyError) as error:
                print(f"Error: {error}")

    @staticmethod
    def _imprimir_lista(
        elementos: Sequence[object], formatear: Callable[[object], str]
    ) -> None:
        if not elementos:
            print("No hay registros cargados.")
            return
        for elemento in elementos:
            print(formatear(elemento))

    @staticmethod
    def _formatear(elemento: object) -> str:
        if isinstance(elemento, Libro):
            return (
                f"[{elemento.id}] {elemento.titulo} | {elemento.autor} | "
                f"ISBN {elemento.isbn} | {elemento.genero.nombre} | "
                f"{elemento.editorial.nombre}"
            )
        if isinstance(elemento, Genero):
            return f"[{elemento.id}] {elemento.nombre}"
        if isinstance(elemento, Editorial):
            return f"[{elemento.id}] {elemento.nombre}"
        if isinstance(elemento, Moneda):
            return (
                f"[{elemento.id}] {elemento.codigo} - {elemento.descripcion}"
            )
        if isinstance(elemento, TipoCotizacion):
            return f"[{elemento.id}] {elemento.nombre}"
        if isinstance(elemento, Precio):
            return (
                f"[{elemento.id}] {elemento.libro.titulo} | "
                f"{elemento.monto:.2f} {elemento.moneda.codigo}"
            )
        if isinstance(elemento, Stock):
            return (
                f"Libro [{elemento.libro.id}] {elemento.libro.titulo}: "
                f"{elemento.cantidad} unidades"
            )
        if isinstance(elemento, CotizacionDolar):
            return (
                f"{elemento.tipo_cotizacion.nombre} | "
                f"{elemento.fecha.isoformat()} | "
                f"${elemento.valor:.2f}"
            )
        return str(elemento)

    @staticmethod
    def _leer_texto(etiqueta: str) -> str:
        return input(etiqueta).strip()

    @staticmethod
    def _leer_entero(etiqueta: str) -> int:
        while True:
            try:
                return int(input(etiqueta).strip())
            except ValueError:
                print("Ingrese un número entero válido.")

    @staticmethod
    def _leer_decimal(etiqueta: str) -> float:
        while True:
            try:
                return float(input(etiqueta).strip().replace(",", "."))
            except ValueError:
                print("Ingrese un número válido.")

    @staticmethod
    def _leer_fecha(etiqueta: str) -> date:
        while True:
            try:
                return date.fromisoformat(
                    input(f"{etiqueta} (AAAA-MM-DD): ").strip()
                )
            except ValueError:
                print("Fecha inválida. Use el formato AAAA-MM-DD.")

    @staticmethod
    def _elegir_id(etiqueta: str, elementos: Sequence[object]) -> int:
        if not elementos:
            raise ValueError(f"No hay {etiqueta.lower()} cargados.")
        for elemento in elementos:
            print(ConsolaBookManager._formatear(elemento))
        return ConsolaBookManager._leer_entero(f"ID de {etiqueta}: ")

    def _crear_genero(self) -> Genero:
        return self._generos.crear(self._leer_texto("Nombre: "))

    def _actualizar_genero(self) -> Genero:
        return self._generos.actualizar(
            self._leer_entero("ID del género: "),
            self._leer_texto("Nuevo nombre: "),
        )

    def _crear_editorial(self) -> Editorial:
        return self._editoriales.crear(self._leer_texto("Nombre: "))

    def _actualizar_editorial(self) -> Editorial:
        return self._editoriales.actualizar(
            self._leer_entero("ID de la editorial: "),
            self._leer_texto("Nuevo nombre: "),
        )

    def _crear_moneda(self) -> Moneda:
        codigo = self._leer_texto("Código (3 letras): ")
        descripcion = self._leer_texto("Descripción: ")
        return self._monedas.crear(codigo, descripcion)

    def _actualizar_moneda(self) -> Moneda:
        identificador = self._leer_entero("ID de la moneda: ")
        codigo = self._leer_texto("Nuevo código: ")
        descripcion = self._leer_texto("Nueva descripción: ")
        return self._monedas.actualizar(identificador, codigo, descripcion)

    def _crear_tipo(self) -> TipoCotizacion:
        return self._tipos.crear(self._leer_texto("Nombre del tipo: "))

    def _actualizar_tipo(self) -> TipoCotizacion:
        identificador = self._leer_entero("ID del tipo: ")
        return self._tipos.actualizar(
            identificador, self._leer_texto("Nuevo nombre: ")
        )

    def _crear_libro(self) -> Libro:
        isbn = self._leer_texto("ISBN: ")
        titulo = self._leer_texto("Título: ")
        autor = self._leer_texto("Autor: ")
        genero_id = self._elegir_id("género", self._generos.listar())
        editorial_id = self._elegir_id("editorial", self._editoriales.listar())
        return self._libros.crear(isbn, titulo, autor, genero_id, editorial_id)

    def _actualizar_libro(self) -> Libro:
        identificador = self._leer_entero("ID del libro: ")
        isbn = self._leer_texto("Nuevo ISBN: ")
        titulo = self._leer_texto("Nuevo título: ")
        autor = self._leer_texto("Nuevo autor: ")
        genero_id = self._elegir_id("género", self._generos.listar())
        editorial_id = self._elegir_id("editorial", self._editoriales.listar())
        return self._libros.actualizar(
            identificador, isbn, titulo, autor, genero_id, editorial_id
        )

    def _crear_precio(self) -> Precio:
        libro_id = self._elegir_id("libro", self._libros.listar())
        monto = self._leer_decimal("Monto: ")
        moneda_id = self._elegir_id("moneda", self._monedas.listar())
        return self._precios.crear(libro_id, monto, moneda_id)

    def _actualizar_precio(self) -> Precio:
        identificador = self._leer_entero("ID del precio: ")
        libro_id = self._elegir_id("libro", self._libros.listar())
        monto = self._leer_decimal("Nuevo monto: ")
        moneda_id = self._elegir_id("moneda", self._monedas.listar())
        return self._precios.actualizar(
            identificador, libro_id, monto, moneda_id
        )

    def _crear_stock(self) -> Stock:
        libro_id = self._elegir_id("libro", self._libros.listar())
        cantidad = self._leer_entero("Cantidad inicial: ")
        return self._stock.crear(libro_id, cantidad)

    def _actualizar_stock(self) -> Stock:
        libro_id = self._leer_entero("ID del libro: ")
        cantidad = self._leer_entero("Nueva cantidad: ")
        return self._stock.actualizar(libro_id, cantidad)

    def _eliminar_stock(self, libro_id: int) -> None:
        self._stock.eliminar(libro_id)

    def _crear_cotizacion(self) -> CotizacionDolar:
        tipo_id = self._elegir_id("tipo de cotización", self._tipos.listar())
        fecha = self._leer_fecha("Fecha")
        valor = self._leer_decimal("Valor del dólar: ")
        return self._cotizaciones.crear(tipo_id, fecha, valor)

    def _actualizar_cotizacion(self) -> CotizacionDolar:
        tipo_id = self._elegir_id("tipo de cotización", self._tipos.listar())
        fecha = self._leer_fecha("Fecha de la cotización a modificar")
        valor = self._leer_decimal("Nuevo valor: ")
        return self._cotizaciones.actualizar(tipo_id, fecha, valor)

    def _eliminar_cotizacion(self, tipo_id: int) -> None:
        fecha = self._leer_fecha("Fecha de la cotización a eliminar")
        self._cotizaciones.eliminar(tipo_id, fecha)

    def _obtener_cotizaciones_api(self) -> None:
        """Descarga y registra las cotizaciones mediante el servicio."""
        self._cotizaciones.obtener_cotizaciones()
        print("Cotizaciones obtenidas y registradas correctamente.")

    def _menu_stock(self) -> None:
        while True:
            print("\n--- Movimientos de stock ---")
            print("1. Ingresar unidades  2. Retirar unidades  0. Volver")
            opcion = input("Opción: ").strip()
            try:
                if opcion == "0":
                    return
                if opcion not in ("1", "2"):
                    print("Opción no válida.")
                    continue
                libro_id = self._elegir_id("libro", self._libros.listar())
                cantidad = self._leer_entero("Cantidad: ")
                stock = (
                    self._stock.ingresar(libro_id, cantidad)
                    if opcion == "1"
                    else self._stock.retirar(libro_id, cantidad)
                )
                print(self._formatear(stock))
            except (ValueError, OSError) as error:
                print(f"Error: {error}")

    def _menu_reportes(self) -> None:
        while True:
            print("\n--- Reportes ---")
            print("1. Catálogo con precios y stock")
            print("2. Libros con stock bajo")
            print("3. Histórico de cotización")
            print("4. Convertir USD a ARS")
            print("5. Lista de precios bimonetaria")
            print("6. Exportar precios a CSV")
            print("0. Volver")
            opcion = input("Opción: ").strip()
            try:
                if opcion == "0":
                    return
                if opcion == "1":
                    self._reporte_catalogo()
                elif opcion == "2":
                    self._reporte_stock_bajo()
                elif opcion == "3":
                    self._reporte_cotizaciones()
                elif opcion == "4":
                    self._reporte_conversion()
                elif opcion == "5":
                    self._reporte_precios_bimonetarios()
                elif opcion == "6":
                    self._exportar_precios_csv()
                else:
                    print("Opción no válida.")
            except (ValueError, OSError) as error:
                print(f"Error: {error}")

    def _reporte_catalogo(self) -> None:
        precios = self._precios.listar()
        stocks = {
            stock.libro.id: stock.cantidad for stock in self._stock.listar()
        }
        if not self._libros.listar():
            print("No hay libros cargados.")
            return
        for libro in self._libros.listar():
            detalle_precios = [
                f"{precio.monto:.2f} {precio.moneda.codigo}"
                for precio in precios
                if precio.libro.id == libro.id
            ]
            texto_precios = (
                ", ".join(detalle_precios) if detalle_precios else "sin precio"
            )
            cantidad = stocks.get(libro.id, 0)
            print(
                f"{self._formatear(libro)} | {texto_precios} | "
                f"Stock: {cantidad}"
            )

    def _reporte_stock_bajo(self) -> None:
        minimo = self._leer_entero(
            "Mostrar libros con stock menor o igual a: "
        )
        encontrados = [
            stock for stock in self._stock.listar() if stock.cantidad <= minimo
        ]
        self._imprimir_lista(encontrados, self._formatear)

    def _reporte_cotizaciones(self) -> None:
        tipo_id = self._elegir_id("tipo de cotización", self._tipos.listar())
        self._imprimir_lista(
            self._cotizaciones.historico(tipo_id), self._formatear
        )

    def _reporte_conversion(self) -> None:
        monto = self._leer_decimal("Monto en USD: ")
        tipo_id = self._elegir_id("tipo de cotización", self._tipos.listar())
        pesos = self._cotizaciones.convertir_a_pesos(monto, tipo_id)
        ultima = self._cotizaciones.ultima(tipo_id)
        print(
            f"USD {monto:.2f} = ARS {pesos:.2f} usando "
            f"{ultima.tipo_cotizacion.nombre} "
            f"del {ultima.fecha.isoformat()} (${ultima.valor:.2f}/USD)."
        )

    def _reporte_precios_bimonetarios(self) -> None:
        """Muestra cada libro con precio ARS y precio en otra moneda."""
        monedas = self._monedas.listar()
        moneda_id = self._elegir_id("moneda distinta de ARS", monedas)
        moneda = self._monedas.obtener(moneda_id)

        if moneda.codigo == "ARS":
            raise ValueError("Seleccione una moneda distinta de ARS.")

        precios_por_libro = {
            (precio.libro.id, precio.moneda.codigo): precio.monto
            for precio in self._precios.listar()
        }
        libros = self._libros.listar()
        if not libros:
            print("No hay libros cargados.")
            return

        print(f"\n--- Precios en ARS y {moneda.codigo} ---")
        for libro in libros:
            ars = precios_por_libro.get((libro.id, "ARS"))
            otra_moneda = precios_por_libro.get((libro.id, moneda.codigo))
            texto_ars = f"ARS {ars:.2f}" if ars is not None else "sin precio ARS"
            texto_otra = (
                f"{moneda.codigo} {otra_moneda:.2f}"
                if otra_moneda is not None
                else f"sin precio {moneda.codigo}"
            )
            print(f"[{libro.id}] {libro.titulo} | {texto_ars} | {texto_otra}")

    def _exportar_precios_csv(self) -> None:
        """Exporta todos los precios registrados, sin filtrar por moneda."""
        ruta_salida = (
            Path(__file__).resolve().parents[3]
            / "precios_todas_las_monedas.csv"
        )
        precios = self._precios.listar()

        with ruta_salida.open("w", newline="", encoding="utf-8") as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(
                ["id_precio", "id_libro", "titulo", "moneda", "monto"]
            )
            for precio in precios:
                escritor.writerow(
                    [
                        precio.id,
                        precio.libro.id,
                        precio.libro.titulo,
                        precio.moneda.codigo,
                        f"{precio.monto:.2f}",
                    ]
                )

        print(f"Se exportaron {len(precios)} precios en: {ruta_salida}")