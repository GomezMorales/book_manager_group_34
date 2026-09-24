"""Servicios con la lógica de negocio de Book Manager."""

from datetime import date
from typing import List, Optional

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


class ServicioGenero:
    """Lógica de negocio para la gestión de géneros."""

    def __init__(self, repo: RepositorioGenero) -> None:
        self._repo = repo

    def _siguiente_id(self) -> int:
        """Devuelve el próximo id disponible (el mayor + 1)."""
        ids = [g.id for g in self._repo.leer_todos()]
        return max(ids, default=0) + 1

    def _validar_nombre(self, nombre: str, id_excluir: Optional[int] = None) -> str:
        """Verifica que el nombre no esté vacío ni repetido."""
        nombre = nombre.strip()
        if not nombre:
            raise ValueError("El nombre del género no puede estar vacío.")
        for g in self._repo.leer_todos():
            if g.nombre.lower() == nombre.lower() and g.id != id_excluir:
                raise ValueError(f"Ya existe el género '{nombre}'.")
        return nombre

    def crear(self, nombre: str) -> Genero:
        """Crea un género con id automático."""
        nombre = self._validar_nombre(nombre)
        return self._repo.crear(Genero(self._siguiente_id(), nombre))

    def listar(self) -> List[Genero]:
        """Devuelve todos los géneros."""
        return self._repo.leer_todos()

    def obtener(self, id: int) -> Genero:
        """Devuelve un género o lanza error si no existe."""
        genero = self._repo.leer_por_id(id)
        if genero is None:
            raise ValueError(f"No existe el género con id {id}.")
        return genero

    def actualizar(self, id: int, nombre: str) -> Genero:
        """Modifica el nombre de un género existente."""
        genero = self.obtener(id)
        genero.nombre = self._validar_nombre(nombre, id_excluir=id)
        return self._repo.actualizar(genero)

    def eliminar(self, id: int) -> None:
        """Elimina un género existente."""
        self.obtener(id)  # valida que exista
        self._repo.eliminar(id)


class ServicioEditorial:
    """Lógica de negocio para la gestión de editoriales."""

    def __init__(self, repo: RepositorioEditorial) -> None:
        self._repo = repo

    def _siguiente_id(self) -> int:
        """Devuelve el próximo id disponible (el mayor + 1)."""
        ids = [e.id for e in self._repo.leer_todos()]
        return max(ids, default=0) + 1

    def _validar_nombre(self, nombre: str, id_excluir: Optional[int] = None) -> str:
        """Verifica que el nombre no esté vacío ni repetido."""
        nombre = nombre.strip()
        if not nombre:
            raise ValueError("El nombre de la editorial no puede estar vacío.")
        for e in self._repo.leer_todos():
            if e.nombre.lower() == nombre.lower() and e.id != id_excluir:
                raise ValueError(f"Ya existe la editorial '{nombre}'.")
        return nombre

    def crear(self, nombre: str) -> Editorial:
        """Crea una editorial con id automático."""
        nombre = self._validar_nombre(nombre)
        return self._repo.crear(Editorial(self._siguiente_id(), nombre))

    def listar(self) -> List[Editorial]:
        """Devuelve todas las editoriales."""
        return self._repo.leer_todos()

    def obtener(self, id: int) -> Editorial:
        """Devuelve una editorial o lanza error si no existe."""
        editorial = self._repo.leer_por_id(id)
        if editorial is None:
            raise ValueError(f"No existe la editorial con id {id}.")
        return editorial

    def actualizar(self, id: int, nombre: str) -> Editorial:
        """Modifica el nombre de una editorial existente."""
        editorial = self.obtener(id)
        editorial.nombre = self._validar_nombre(nombre, id_excluir=id)
        return self._repo.actualizar(editorial)

    def eliminar(self, id: int) -> None:
        """Elimina una editorial existente."""
        self.obtener(id)  # valida que exista
        self._repo.eliminar(id)


class ServicioTipoCotizacion:
    """Lógica de negocio para la gestión de tipos de cotización."""

    def __init__(self, repo: RepositorioTipoCotizacion) -> None:
        self._repo = repo

    def _siguiente_id(self) -> int:
        """Devuelve el próximo id disponible (el mayor + 1)."""
        ids = [t.id for t in self._repo.leer_todos()]
        return max(ids, default=0) + 1

    def _validar_nombre(self, nombre: str, id_excluir: Optional[int] = None) -> str:
        """Verifica que el nombre no esté vacío ni repetido."""
        nombre = nombre.strip()
        if not nombre:
            raise ValueError("El nombre del tipo de cotización no puede estar vacío.")
        for t in self._repo.leer_todos():
            if t.nombre.lower() == nombre.lower() and t.id != id_excluir:
                raise ValueError(f"Ya existe el tipo de cotización '{nombre}'.")
        return nombre

    def crear(self, nombre: str) -> TipoCotizacion:
        """Crea un tipo de cotización con id automático."""
        nombre = self._validar_nombre(nombre)
        return self._repo.crear(TipoCotizacion(self._siguiente_id(), nombre))

    def listar(self) -> List[TipoCotizacion]:
        """Devuelve todos los tipos de cotización."""
        return self._repo.leer_todos()

    def obtener(self, id: int) -> TipoCotizacion:
        """Devuelve un tipo de cotización o lanza error si no existe."""
        tipo = self._repo.leer_por_id(id)
        if tipo is None:
            raise ValueError(f"No existe el tipo de cotización con id {id}.")
        return tipo

    def actualizar(self, id: int, nombre: str) -> TipoCotizacion:
        """Modifica el nombre de un tipo de cotización existente."""
        tipo = self.obtener(id)
        tipo.nombre = self._validar_nombre(nombre, id_excluir=id)
        return self._repo.actualizar(tipo)

    def eliminar(self, id: int) -> None:
        """Elimina un tipo de cotización existente."""
        self.obtener(id)  # valida que exista
        self._repo.eliminar(id)


class ServicioMoneda:
    """Lógica de negocio para la gestión de monedas."""

    def __init__(self, repo: RepositorioMoneda) -> None:
        self._repo = repo

    def _siguiente_id(self) -> int:
        """Devuelve el próximo id disponible (el mayor + 1)."""
        ids = [m.id for m in self._repo.leer_todos()]
        return max(ids, default=0) + 1

    def _validar_codigo(self, codigo: str, id_excluir: Optional[int] = None) -> str:
        """Verifica que el código tenga 3 letras (ej. ARS, USD) y no esté repetido."""
        codigo = codigo.strip().upper()
        if len(codigo) != 3 or not codigo.isalpha():
            raise ValueError("El código de moneda debe tener 3 letras (ej. ARS, USD).")
        for m in self._repo.leer_todos():
            if m.codigo == codigo and m.id != id_excluir:
                raise ValueError(f"Ya existe la moneda con código '{codigo}'.")
        return codigo

    def _validar_descripcion(self, descripcion: str) -> str:
        """Verifica que la descripción no esté vacía."""
        descripcion = descripcion.strip()
        if not descripcion:
            raise ValueError("La descripción de la moneda no puede estar vacía.")
        return descripcion

    def crear(self, codigo: str, descripcion: str) -> Moneda:
        """Crea una moneda con id automático."""
        codigo = self._validar_codigo(codigo)
        descripcion = self._validar_descripcion(descripcion)
        return self._repo.crear(Moneda(self._siguiente_id(), codigo, descripcion))

    def listar(self) -> List[Moneda]:
        """Devuelve todas las monedas."""
        return self._repo.leer_todos()

    def obtener(self, id: int) -> Moneda:
        """Devuelve una moneda o lanza error si no existe."""
        moneda = self._repo.leer_por_id(id)
        if moneda is None:
            raise ValueError(f"No existe la moneda con id {id}.")
        return moneda

    def actualizar(self, id: int, codigo: str, descripcion: str) -> Moneda:
        """Modifica el código y la descripción de una moneda existente."""
        moneda = self.obtener(id)
        moneda.codigo = self._validar_codigo(codigo, id_excluir=id)
        moneda.descripcion = self._validar_descripcion(descripcion)
        return self._repo.actualizar(moneda)

    def eliminar(self, id: int) -> None:
        """Elimina una moneda existente."""
        self.obtener(id)  # valida que exista
        self._repo.eliminar(id)

      
class ServicioLibro:
    """Lógica de negocio para la gestión de libros."""

    def __init__(
        self,
        repo: RepositorioLibro,
        repo_genero: RepositorioGenero,
        repo_editorial: RepositorioEditorial,
    ) -> None:
        self._repo = repo
        self._repo_genero = repo_genero
        self._repo_editorial = repo_editorial

    def _siguiente_id(self) -> int:
        """Devuelve el próximo id disponible (el mayor + 1)."""
        ids = [l.id for l in self._repo.leer_todos()]
        return max(ids, default=0) + 1

    def _validar_isbn(self, isbn: str, id_excluir: Optional[int] = None) -> str:
        """Verifica que el ISBN tenga 10 o 13 dígitos y no esté repetido."""
        isbn = isbn.replace("-", "").strip()  # acepta "978-950-..." y lo guarda sin guiones
        if not isbn.isdigit() or len(isbn) not in (10, 13):
            raise ValueError("El ISBN debe tener 10 o 13 dígitos.")
        for l in self._repo.leer_todos():
            if l.isbn == isbn and l.id != id_excluir:
                raise ValueError(f"Ya existe un libro con ISBN {isbn}.")
        return isbn

    def _validar_texto(self, valor: str, campo: str) -> str:
        """Verifica que un campo de texto no esté vacío."""
        valor = valor.strip()
        if not valor:
            raise ValueError(f"El {campo} del libro no puede estar vacío.")
        return valor

    def _obtener_genero(self, genero_id: int) -> Genero:
        """Devuelve el género o lanza error si no existe."""
        genero = self._repo_genero.leer_por_id(genero_id)
        if genero is None:
            raise ValueError(f"No existe el género con id {genero_id}.")
        return genero

    def _obtener_editorial(self, editorial_id: int) -> Editorial:
        """Devuelve la editorial o lanza error si no existe."""
        editorial = self._repo_editorial.leer_por_id(editorial_id)
        if editorial is None:
            raise ValueError(f"No existe la editorial con id {editorial_id}.")
        return editorial

    def crear(
        self, isbn: str, titulo: str, autor: str, genero_id: int, editorial_id: int
    ) -> Libro:
        """Crea un libro con id automático, validando sus datos y relaciones."""
        libro = Libro(
            self._siguiente_id(),
            self._validar_isbn(isbn),
            self._validar_texto(titulo, "título"),
            self._validar_texto(autor, "autor"),
            self._obtener_genero(genero_id),
            self._obtener_editorial(editorial_id),
        )
        return self._repo.crear(libro)

    def listar(self) -> List[Libro]:
        """Devuelve todos los libros."""
        return self._repo.leer_todos()

    def obtener(self, id: int) -> Libro:
        """Devuelve un libro o lanza error si no existe."""
        libro = self._repo.leer_por_id(id)
        if libro is None:
            raise ValueError(f"No existe el libro con id {id}.")
        return libro

    def actualizar(
        self, id: int, isbn: str, titulo: str, autor: str, genero_id: int, editorial_id: int
    ) -> Libro:
        """Modifica todos los datos de un libro existente."""
        libro = self.obtener(id)
        libro.isbn = self._validar_isbn(isbn, id_excluir=id)
        libro.titulo = self._validar_texto(titulo, "título")
        libro.autor = self._validar_texto(autor, "autor")
        libro.genero = self._obtener_genero(genero_id)
        libro.editorial = self._obtener_editorial(editorial_id)
        return self._repo.actualizar(libro)

    def eliminar(self, id: int) -> None:
        """Elimina un libro existente."""
        self.obtener(id)  # valida que exista
        self._repo.eliminar(id)


class ServicioPrecio:
    """Lógica de negocio para la gestión de precios."""

    def __init__(
        self,
        repo: RepositorioPrecio,
        repo_libro: RepositorioLibro,
        repo_moneda: RepositorioMoneda,
    ) -> None:
        self._repo = repo
        self._repo_libro = repo_libro
        self._repo_moneda = repo_moneda

    def _siguiente_id(self) -> int:
        """Devuelve el próximo id disponible (el mayor + 1)."""
        ids = [p.id for p in self._repo.leer_todos()]
        return max(ids, default=0) + 1

    def _validar_monto(self, monto: float) -> float:
        """Verifica que el monto sea mayor a cero."""
        if monto <= 0:
            raise ValueError("El monto del precio debe ser mayor a cero.")
        return float(monto)

    def _obtener_libro(self, libro_id: int) -> Libro:
        """Devuelve el libro o lanza error si no existe."""
        libro = self._repo_libro.leer_por_id(libro_id)
        if libro is None:
            raise ValueError(f"No existe el libro con id {libro_id}.")
        return libro

    def _obtener_moneda(self, moneda_id: int) -> Moneda:
        """Devuelve la moneda o lanza error si no existe."""
        moneda = self._repo_moneda.leer_por_id(moneda_id)
        if moneda is None:
            raise ValueError(f"No existe la moneda con id {moneda_id}.")
        return moneda

    def _validar_unico(self, libro_id: int, moneda_id: int, id_excluir: Optional[int] = None) -> None:
        """Verifica que el libro no tenga ya un precio en esa moneda."""
        for p in self._repo.leer_todos():
            if p.libro.id == libro_id and p.moneda.id == moneda_id and p.id != id_excluir:
                raise ValueError("El libro ya tiene un precio en esa moneda.")

    def crear(self, libro_id: int, monto: float, moneda_id: int) -> Precio:
        """Crea un precio con id automático, validando sus datos y relaciones."""
        monto = self._validar_monto(monto)
        libro = self._obtener_libro(libro_id)
        moneda = self._obtener_moneda(moneda_id)
        self._validar_unico(libro_id, moneda_id)
        precio = Precio(self._siguiente_id(), libro, monto, moneda)
        return self._repo.crear(precio)

    def listar(self) -> List[Precio]:
        """Devuelve todos los precios."""
        return self._repo.leer_todos()

    def obtener(self, id: int) -> Precio:
        """Devuelve un precio o lanza error si no existe."""
        precio = self._repo.leer_por_id(id)
        if precio is None:
            raise ValueError(f"No existe el precio con id {id}.")
        return precio

    def actualizar(self, id: int, libro_id: int, monto: float, moneda_id: int) -> Precio:
        """Modifica todos los datos de un precio existente."""
        precio = self.obtener(id)
        precio.monto = self._validar_monto(monto)
        precio.libro = self._obtener_libro(libro_id)
        precio.moneda = self._obtener_moneda(moneda_id)
        self._validar_unico(libro_id, moneda_id, id_excluir=id)
        return self._repo.actualizar(precio)

    def eliminar(self, id: int) -> None:
        """Elimina un precio existente."""
        self.obtener(id)  # valida que exista
        self._repo.eliminar(id)


class ServicioStock:
    """Lógica de negocio para la gestión del stock de libros."""

    def __init__(self, repo: RepositorioStock, repo_libro: RepositorioLibro) -> None:
        self._repo = repo
        self._repo_libro = repo_libro

    def _validar_cantidad(self, cantidad: int) -> int:
        """Verifica que la cantidad sea un entero no negativo."""
        if not isinstance(cantidad, int) or cantidad < 0:
            raise ValueError("La cantidad debe ser un número entero mayor o igual a cero.")
        return cantidad

    def _obtener_libro(self, libro_id: int) -> Libro:
        """Devuelve el libro o lanza error si no existe."""
        libro = self._repo_libro.leer_por_id(libro_id)
        if libro is None:
            raise ValueError(f"No existe el libro con id {libro_id}.")
        return libro

    def crear(self, libro_id: int, cantidad: int) -> Stock:
        """Registra el stock inicial de un libro."""
        cantidad = self._validar_cantidad(cantidad)
        libro = self._obtener_libro(libro_id)
        if self._repo.leer_por_libro(libro_id) is not None:
            raise ValueError(f"El libro con id {libro_id} ya tiene stock registrado.")
        return self._repo.crear(Stock(libro, cantidad))

    def listar(self) -> List[Stock]:
        """Devuelve el stock de todos los libros que lo tengan registrado."""
        stocks = []
        for libro in self._repo_libro.leer_todos():
            stock = self._repo.leer_por_libro(libro.id)
            if stock is not None:
                stocks.append(stock)
        return stocks

    def obtener(self, libro_id: int) -> Stock:
        """Devuelve el stock de un libro o lanza error si no existe."""
        stock = self._repo.leer_por_libro(libro_id)
        if stock is None:
            raise ValueError(f"No hay stock registrado para el libro con id {libro_id}.")
        return stock

    def actualizar(self, libro_id: int, cantidad: int) -> Stock:
        """Reemplaza la cantidad en stock de un libro."""
        stock = self.obtener(libro_id)
        stock.cantidad = self._validar_cantidad(cantidad)
        return self._repo.actualizar(stock)

    def ingresar(self, libro_id: int, cantidad: int) -> Stock:
        """Suma unidades al stock (por ejemplo, al recibir mercadería)."""
        if self._validar_cantidad(cantidad) == 0:
            raise ValueError("La cantidad a ingresar debe ser mayor a cero.")
        stock = self.obtener(libro_id)
        stock.cantidad += cantidad
        return self._repo.actualizar(stock)

    def retirar(self, libro_id: int, cantidad: int) -> Stock:
        """Resta unidades al stock (por ejemplo, al vender), sin quedar negativo."""
        if self._validar_cantidad(cantidad) == 0:
            raise ValueError("La cantidad a retirar debe ser mayor a cero.")
        stock = self.obtener(libro_id)
        if cantidad > stock.cantidad:
            raise ValueError(
                f"Stock insuficiente: hay {stock.cantidad} y se quieren retirar {cantidad}."
            )
        stock.cantidad -= cantidad
        return self._repo.actualizar(stock)

    def eliminar(self, libro_id: int) -> None:
        """Elimina el registro de stock de un libro."""
        self.obtener(libro_id)  # valida que exista
        self._repo.eliminar(libro_id)


class ServicioCotizacionDolar:
    """Lógica de negocio para la gestión de cotizaciones del dólar."""

    def __init__(
        self,
        repo: RepositorioCotizacionDolar,
        repo_tipo: RepositorioTipoCotizacion,
    ) -> None:
        self._repo = repo
        self._repo_tipo = repo_tipo

    def _validar_valor(self, valor: float) -> float:
        """Verifica que el valor sea mayor a cero."""
        if valor <= 0:
            raise ValueError("El valor de la cotización debe ser mayor a cero.")
        return float(valor)

    def _validar_fecha(self, fecha: date) -> date:
        """Verifica que la fecha no sea futura."""
        if fecha > date.today():
            raise ValueError("La fecha de la cotización no puede ser futura.")
        return fecha

    def _obtener_tipo(self, tipo_id: int) -> TipoCotizacion:
        """Devuelve el tipo de cotización o lanza error si no existe."""
        tipo = self._repo_tipo.leer_por_id(tipo_id)
        if tipo is None:
            raise ValueError(f"No existe el tipo de cotización con id {tipo_id}.")
        return tipo

    def crear(self, tipo_id: int, fecha: date, valor: float) -> CotizacionDolar:
        """Registra la cotización de un tipo de dólar en una fecha."""
        valor = self._validar_valor(valor)
        fecha = self._validar_fecha(fecha)
        tipo = self._obtener_tipo(tipo_id)
        if self._repo.leer_por_tipo_y_fecha(tipo_id, fecha) is not None:
            raise ValueError(f"Ya existe una cotización de {tipo.nombre} para el {fecha}.")
        return self._repo.crear(CotizacionDolar(tipo, fecha, valor))

    def listar(self) -> List[CotizacionDolar]:
        """Devuelve todas las cotizaciones de todos los tipos."""
        cotizaciones = []
        for tipo in self._repo_tipo.leer_todos():
            cotizaciones.extend(self._repo.leer_historico_por_tipo(tipo.id))
        return cotizaciones

    def obtener(self, tipo_id: int, fecha: date) -> CotizacionDolar:
        """Devuelve una cotización o lanza error si no existe."""
        cotizacion = self._repo.leer_por_tipo_y_fecha(tipo_id, fecha)
        if cotizacion is None:
            raise ValueError(f"No hay cotización del tipo {tipo_id} para el {fecha}.")
        return cotizacion

    def historico(self, tipo_id: int) -> List[CotizacionDolar]:
        """Devuelve las cotizaciones de un tipo, ordenadas por fecha."""
        self._obtener_tipo(tipo_id)  # valida que el tipo exista
        return sorted(self._repo.leer_historico_por_tipo(tipo_id), key=lambda c: c.fecha)

    def ultima(self, tipo_id: int) -> CotizacionDolar:
        """Devuelve la cotización más reciente de un tipo."""
        historico = self.historico(tipo_id)
        if not historico:
            raise ValueError(f"No hay cotizaciones cargadas para el tipo {tipo_id}.")
        return historico[-1]

    def actualizar(self, tipo_id: int, fecha: date, valor: float) -> CotizacionDolar:
        """Modifica el valor de una cotización existente."""
        cotizacion = self.obtener(tipo_id, fecha)
        cotizacion.valor = self._validar_valor(valor)
        return self._repo.actualizar(cotizacion)

    def eliminar(self, tipo_id: int, fecha: date) -> None:
        """Elimina una cotización existente."""
        self.obtener(tipo_id, fecha)  # valida que exista
        self._repo.eliminar(tipo_id, fecha)

    def convertir_a_pesos(self, monto_usd: float, tipo_id: int) -> float:
        """Convierte un monto en dólares a pesos con la última cotización del tipo."""
        return round(monto_usd * self.ultima(tipo_id).valor, 2)
