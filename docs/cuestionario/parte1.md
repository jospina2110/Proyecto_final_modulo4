# Parte 1. Bases de datos — Preguntas teóricas

1. **¿Qué es una base de datos relacional y cuáles son sus principales características?**
   Es una base de datos que organiza la información en **tablas** formadas por filas (registros) y columnas (campos), donde las tablas se relacionan entre sí mediante **claves primarias y foráneas**. Sus características principales son: esquema fijo definido antes de guardar datos, uso de **SQL** para consultar, integridad de los datos, soporte de **transacciones ACID** (atomicidad, consistencia, aislamiento y durabilidad) y normalización para evitar duplicidad. Por ejemplo, en un sistema de citas habría una tabla `pacientes`, una tabla `medicos` y una tabla `citas` que apunta a las dos anteriores.

2. **¿Cuál es la diferencia entre una base de datos relacional y una no relacional?**
   Una base de datos **relacional** (MySQL, PostgreSQL) guarda todo en tablas con esquema fijo y relaciona la información con claves foráneas. Una base de datos **no relacional** o NoSQL (MongoDB) no usa tablas ni esquema fijo: agrupa la información en estructuras flexibles (en MongoDB, **documentos** en formato BSON dentro de **colecciones**) y no maneja claves foráneas ni JOIN nativos. Lo NoSQL suele escalar horizontalmente con más facilidad, mientras que lo relacional suele ofrecer mayor consistencia transaccional. En este proyecto usamos MongoDB: cada cita es un documento que referencia al paciente y al médico por su `_id` en lugar de usar claves foráneas.

3. **Explique la diferencia entre WHERE y HAVING en SQL.**
   `WHERE` filtra **filas individuales antes de agrupar**, mientras que `HAVING` filtra **grupos después de un GROUP BY**, normalmente usando funciones de agregación. Por ejemplo, `WHERE estado = 'pendiente'` deja solo las filas de citas pendientes, pero `HAVING COUNT(*) > 5` deja solo los médicos que quedaron con más de 5 citas tras agrupar. La idea de "filtrar antes" y "filtrar después" existe también en MongoDB: `$match` antes de `$group` y `$match` después de `$group` en una agregación.

4. **¿Qué función cumple una clave primaria (PRIMARY KEY)?**
   Es el campo (o combinación de campos) que **identifica de manera única** cada fila de una tabla. No puede repetirse ni ser nulo, y crea automáticamente un índice que acelera las búsquedas. Otras tablas la usan como referencia a través de claves foráneas: por ejemplo, la tabla `citas` guarda el id del paciente y el id del médico. En MongoDB el equivalente es el campo `_id`.

5. **¿Cuál es la diferencia entre INNER JOIN y LEFT JOIN?**
   `INNER JOIN` devuelve **solo las filas que coinciden en ambas tablas**; `LEFT JOIN` devuelve **todas las filas de la tabla izquierda** aunque no tengan coincidencia, rellenando con `NULL` las columnas de la derecha. Por ejemplo, al unir pacientes con citas: con INNER JOIN los pacientes sin citas no aparecen; con LEFT JOIN aparecen con los campos de cita en `NULL`. En MongoDB no existen JOIN como tales, lo más parecido es `$lookup` en una agregación; en este proyecto las citas guardan referencias y se resuelven con consultas adicionales.

6. **Explique la diferencia entre DELETE, TRUNCATE y DROP.**
   `DELETE` elimina **filas específicas** según una condición (`WHERE`), registra cada borrado y puede revertirse dentro de una transacción. `TRUNCATE` **vacía toda la tabla** de manera rápida, sin permitir `WHERE`. `DROP` va más allá: **elimina la tabla completa con su estructura**, por lo que deja de existir. Una diferencia práctica que aplicamos en el proyecto: para cancelar una cita **no** hacemos un borrado físico con DELETE, sino un **cambio de estado** a "cancelada", para conservar el historial del paciente.

7. **¿Qué es MongoDB y qué tipo de base de datos utiliza?**
   MongoDB es un sistema de gestión de bases de datos **NoSQL orientado a documentos**. Guarda la información en documentos con formato **BSON** (una representación binaria similar a JSON) agrupados en colecciones. No exige un esquema fijo, permite estructuras anidadas (subdocumentos y arreglos) y está diseñado para escalar horizontalmente mediante réplicas y sharding. En este proyecto almacena las colecciones `patients`, `doctors` y `appointments`.

8. **¿Cuál es la diferencia entre una colección y un documento en MongoDB?**
   Una **colección** es un conjunto de documentos, parecido al concepto de tabla en el modelo relacional. Un **documento** es un registro individual dentro de la colección, parecido a una fila, pero con estructura flexible: cada documento puede tener campos distintos y valores anidados. Por ejemplo, `appointments` es la colección y cada cita (con `patient_id`, `doctor_id`, `scheduled_at`, `status`...) es un documento.

9. **¿Qué representa el campo _id en MongoDB?**
   Es el **identificador único** de cada documento dentro de su colección; cumple el papel de clave primaria. Si no se define manualmente, MongoDB lo genera automáticamente como un **ObjectId**, un valor de 12 bytes que incluye marca de tiempo, un componente aleatorio y un contador, lo que prácticamente garantiza que sea único. En el proyecto, `_id` se usa para referenciar al paciente y al médico desde cada cita.

10. **¿Qué criterios tendría en cuenta para seleccionar MySQL o MongoDB para un sistema de gestión de citas médicas?**
    Tendría en cuenta varios criterios: la **estructura de los datos** (si son muy relacionales y estables, MySQL; si el esquema va a evolucionar, MongoDB), la necesidad de **transacciones ACID** estrictas, la **cantidad y complejidad de relaciones** (muchos JOIN → MySQL), los **requisitos de escalabilidad** (MongoDB escala horizontalmente con más facilidad), el **ecosistema y la experiencia del equipo**, y los **costos operativos**. Para este proyecto elegimos MongoDB porque las citas se modelan de forma natural como documentos con referencias a paciente y médico, y el esquema puede crecer sin migraciones rígidas.
