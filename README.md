# Book Manager

## Sprint 3

### Objetivo
Aplicar los conocimientos de programación orientada a objetos, persistencia en base de datos y obtención de datos desde la web.

### Introducción y contexto
En este sprint se descargan y procesan datos de la web (scraping de Cúspide con Scrapy) para comparar los precios internos con los de la competencia, generar alertas y reportes en Excel, y auditar cada operación del sistema.

### Comparación de precios y auditoría

Desde **Reportes → Comparación de precios web a Excel** se genera un archivo
`.xlsx` con el libro, el precio interno, el precio web, la diferencia y la fecha
de extracción. El archivo queda guardado en `src/book_manager/reportes/`.
Se puede ejecutar el scraper antes de generar el reporte o reutilizar su última
extracción.

Las operaciones públicas de los servicios se registran en la tabla `auditoria`
con la acción, la fecha, los argumentos relevantes y el resultado. El historial
se consulta desde la opción **Historial de auditoría** del menú principal.
