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

Para evitar alertas de libros que no corresponden a la búsqueda, los títulos
web se comparan con el título del catálogo y solo se aceptan coincidencias con
similitud mínima de `0.75`. También se admiten coincidencias exactas con
formatos editoriales reconocidos, como “tapa dura” o “bolsillo”; no alcanza con
que el título buscado aparezca dentro de otro título, y se exige que coincidan
los números que forman parte del título. Este filtro se aplica tanto durante
el scraping como al generar alertas y reportes.

### Menú principal (Sprint 3)

- **13. Ejecutar scraping**: pide la diferencia de precio (%) a partir de la
  cual alertar, ejecuta el scraper de Cúspide y genera
  `src/book_manager/reportes/alertas_AAAAMMDD_HHMMSS.csv`.
- **14. Generar reporte Excel**: comparación de precios internos y web.
- **12. Historial de auditoría**: operaciones registradas en la tabla `auditoria`.
