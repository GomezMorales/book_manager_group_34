# Sprint 3

## [Ejercicio 07]
- Se agregan al menú principal las opciones "Ejecutar scraping" (pide la diferencia de precio, ejecuta el scraper y genera el CSV de alertas) y "Generar reporte Excel".
- Se mantiene "Historial de auditoría" en el menú principal.
- Se agregan los alias *Model en models.py, RepositorioAuditoria en repositories.py y se reexporta ServicioAuditoria desde services.py.
- Ajustes de estilo PEP8 en scraper, servicios y consola.

## [Ejercicio 06]
- Se agrega el decorador de auditoría en services/auditoria.py para registrar las operaciones públicas de los servicios.
- Se crea la tabla auditoria con acción, fecha y detalles; se registran tanto las operaciones exitosas como las fallidas.
- Se agrega la opción para consultar el historial de auditoría desde el menú principal.

## [Ejercicio 05]
- Se agrega la generación de reportes Excel con el libro, el precio interno, el precio web, la diferencia y la fecha de extracción.
- Los reportes se guardan en src/book_manager/reportes/ con nombre único por ejecución.
- Se incorpora la opción de generar el reporte desde el menú de reportes, ejecutando el scraper o reutilizando la última extracción.

## [Ejercicio 04]
- Se agrega services/alertas.py con ServicioAlertasPrecio.
- generar_alertas(umbral) recibe la diferencia de precio (%) ingresada por el usuario, ejecuta el scraper y compara los precios.
- Se compara el precio interno en ARS de cada libro con el resultado más parecido obtenido en Cúspide.
- Cada ejecución genera un CSV descargable reportes/alertas_AAAAMMDD_HHMMSS.csv y devuelve las alertas y la ruta del archivo.

## [Ejercicio 03]
- Se implementa el módulo `book_manager.scraper` utilizando Scrapy para obtener información de libros desde Cúspide.
- Se crea `CuspideSpider`, que recibe títulos del catálogo y procesa como máximo 10 resultados por cada búsqueda.
- Se implementan `Item`, `ItemLoader` y pipelines para limpiar datos, validar registros, evitar duplicados y exportar resultados en formato JSONL.
- Se incorporan los datos de precio, URL de imagen, medios de pago, descripción, URL del producto y fecha de extracción.
- Se agrega `scrapy.cfg` y las dependencias necesarias para ejecutar el scraper.

## [Ejercicio 02]
- Se agrega cargar_datos_desde_sql en migrations/migrations.py.
- Ejecuta los .sql en orden de claves foráneas dentro de una única transacción.
- La carga es repetible: usa ON CONFLICT DO NOTHING y reinicia las secuencias.

## [Ejercicio 01]
- Se crea la rama Sprint_3 a partir de Sprint_2.
- Se agregan las carpetas scraper y reportes.
- Se agregan scrapy y openpyxl a requirements.txt.
- Se actualiza el README al Sprint 3.

# Sprint 2

## [Ejercicio 08]
- Se modifica book_manager/ui/console.py para extender el menú principal y sus opciones.

## [Ejercicio 07]
- Se modifica el .env para poder obtener la URL de la API y se crean las funciones para descargar, buscar y registrar las cotizaciones en la base de datos.

## [Ejercicio 06]
- Se migra la persistencia con la que trabaja el sistema, pasando de operar con los CSV a operar con la BBDD definida en los ejercicios previos.

## [Ejercicio 05]
- Se implementa migrar_datos en migrations/migrations.py: lee los CSV del Sprint 1 y genera un archivo .sql por tabla en migrations/sql.
- Los .sql se ejecutan en una única transacción y en orden de dependencias (claves foráneas); la migración se puede repetir sin duplicar datos (ON CONFLICT DO NOTHING).
- Se crean las tablas si no existen y se reinician las secuencias de PostgreSQL para que los próximos altas no choquen con los ids migrados.
- Se agrega .gitignore para excluir los archivos __pycache__.

## [Ejercicio 04]
- Se definen e implementan las tablas utilizando el ORM de SQLAlchemy para migrar los datos de archivos csv a un modelo de bbdd relacional.

## [Ejercicio 03]
- Se implementa la clase Transaccion en database/connection.py como context manager (__enter__ y __exit__).
- Al salir del bloque with confirma los cambios (commit) o los deshace (rollback) ante un error, y siempre cierra la sesión.
- Se agrega el método transaccion() a ConexionDB para usarlo con with.

## [Ejercicio 02]
- Se implementa la clase ConexionDB en database/connection.py usando SQLAlchemy.
- La URL de conexión se lee del archivo .env y la contraseña de la variable de entorno DATABASE_PASSWORD.
- Se agregan SQLAlchemy, python-dotenv y psycopg2-binary a requirements.txt.

## [Ejercicio 01]
- Se crea la rama Sprint_2 a partir de Sprint_1.
- Se agregan database/connection.py, models/models.py, migrations/sql y .env.
- Se actualiza el README al Sprint 2.

# Sprint 1

## [Ejercicio 07]
- Ajustes de estilo PEP8 en todos los módulos (indentación de 4 espacios, líneas de hasta 79 caracteres, nombres descriptivos) sin cambios funcionales.
- Se implementa la ejecución del programa en main.py  

## [Ejercicio 06]
- Se implementa el menú principal y los submenús de cada item  

## [Ejercicio 05]
- Se implementa cargar_datos_iniciales en preload_data.py, que genera los CSV usando los servicios.
- Se cargan 10 géneros, editoriales, monedas, tipos de cotización, libros y registros de stock.
- Se cargan 20 precios (ARS y USD) y 12 cotizaciones del dólar.

## [Ejercicio 04]
- Se implementa un servicio por entidad con CRUD completo, validaciones e id automático.
- ServicioLibro y ServicioPrecio validan que existan sus entidades relacionadas.
- ServicioStock agrega ingreso y retiro de unidades sin permitir stock negativo.
- ServicioCotizacionDolar agrega histórico, última cotización y conversión de USD a pesos.
- Se impide eliminar entidades que estén en uso por otras.

## [Ejercicio 03]
- Se definen las interfaces IRepositorio, IRepositorioStock e IRepositorioCotizacionDolar.
- Se implementan RepositorioGenero, RepositorioEditorial, RepositorioMoneda y RepositorioTipoCotizacion.
- Se implementan RepositorioLibro y RepositorioPrecio con resolución de relaciones entre objetos.
- Se implementan RepositorioStock y RepositorioCotizacionDolar con sus interfaces específicas.

## [Ejercicio 02]
- Se crea EntidadBase y las clases entidad: Libro, Genero, Editorial, Moneda, TipoCotizacion, Precio, Stock y CotizacionDolar, con encapsulación y relaciones entre objetos.

## [Ejercicio 01]
- Se clona el repositorio y se crea la rama Sprint_1.
- Se crea la estructura de carpetas y archivos base del proyecto.
