# Book Manager

## Sprint 2

### Objetivo
Consolidar las bases de manejo de bases de datos, normalización, conexión segura y carga inicial, aplicando programación orientada a objetos.

### Introducción y contexto
En esta segunda entrega ampliamos el alcance haciendo que la aplicación persista en una base de datos relacional, utilizando el ORM SQLAlchemy.

La idea principal es migrar todos los datos cargados en los archivos CSV a tablas relacionales.

Además se realizan consultas a APIs externas.

### Ejecución y persistencia

La aplicación utiliza SQLAlchemy para leer y escribir en la base de datos
configurada mediante `DATABASE_URL` en el archivo `.env`. Los repositorios,
servicios y la interfaz de consola conservan las mismas operaciones CRUD; los
CSV de `src/book_manager/migrations/csv` ya no se utilizan durante la ejecución
normal.

Para cargar los datos de ejemplo se puede iniciar la aplicación llamando a
`main(import_default_data=True)`. Esta opción reemplaza los datos de las tablas
con el conjunto inicial y debe utilizarse solo cuando se desee reinicializar
la base de datos.