# Parte 3. ORM y acceso a datos — Preguntas teóricas

> Nota: el enunciado permite, al elegir MongoDB, una alternativa de acceso a datos compatible
> con la base seleccionada. En este proyecto se usa **Beanie** como ODM. Las preguntas sobre
> Prisma se responden de forma teórica.

44. **¿Qué es un ORM y qué problema busca solucionar?**
    Un ORM (Object-Relational Mapping) es una herramienta que **mapea los objetos del lenguaje de programación a las estructuras de la base de datos**, para no escribir consultas manuales todo el tiempo. Busca solucionar: la repetición de código SQL, la traducción de tipos entre lenguaje y base de datos, el manejo de relaciones y la protección contra errores comunes como la inyección de consultas. Cuando la base es de documentos (MongoDB) la herramienta equivalente se llama **ODM** (Object-Document Mapping), como Beanie en este proyecto.

45. **¿Qué es Prisma y cómo facilita el acceso a una base de datos?**
    Prisma es un ORM moderno para **Node.js/TypeScript**. Facilita el acceso porque se declara el esquema una sola vez en un archivo (`schema.prisma`), y a partir de él Prisma **genera un cliente tipado** con el que se consulta la base mediante métodos (`findMany`, `create`, `update`) en lugar de escribir SQL a mano, además de ofrecer autocompletado y detección de errores en el editor. En este proyecto usamos Beanie como alternativa permitida (Python), pero el concepto es exactamente el mismo: modelos declarados + cliente generado.

46. **¿Qué función cumple el archivo schema.prisma?**
    Es el **archivo central de configuración de Prisma**: en él se declaran la fuente de datos (`datasource`, la conexión a la base), el generador (`generator client`) y los **modelos con sus campos y relaciones**. Es la única fuente de verdad del esquema: cuando cambia, Prisma sabe cómo generar el cliente y qué migraciones aplicar. Su equivalente en este proyecto son las clases de `app/models/` (Patient, Doctor y Appointment escritas con Beanie).

47. **¿Qué es una migración y para qué sirve?**
    Una migración es un **cambio versionado del esquema de la base de datos** (crear una tabla, añadir un campo, cambiar un tipo, etc.), guardado como un script que se puede aplicar en orden. Sirve para que la base evolucione de forma **controlada y reproducible**: todos los entornos (desarrollo, pruebas, producción) quedan con el mismo esquema y el equipo no tiene que alterar las bases manualmente ni "adivinar" qué cambió.

48. **¿Cuál es la diferencia entre Prisma Client y Prisma Migrate?**
    **Prisma Client** es la librería generada que se usa **en tiempo de ejecución** para consultar y modificar datos desde el código (es el "ORM" que usa la aplicación). **Prisma Migrate** es la herramienta de **línea de comandos** que compara `schema.prisma` con la base real y genera/aplica las **migraciones** para actualizar la estructura. En resumen: uno sirve para operar con los datos y el otro para versionar el esquema.
