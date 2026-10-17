# Parte 6. Pipelines CI/CD — Preguntas teóricas

77. **¿Qué es la integración continua (CI)?**
    Es la práctica de **integrar con frecuencia los cambios del equipo en un repositorio común**, donde cada integración (push o pull request) dispara automáticamente una serie de verificaciones: instalar dependencias, ejecutar pruebas, análisis de calidad. Su objetivo es **detectar errores lo antes posible**, cuando son más baratos de corregir. En este proyecto, cada push a `main` o pull request ejecuta la etapa de pruebas con pytest.

78. **¿Qué es la entrega o el despliegue continuo (CD)?**
    La **entrega continua** significa que, después de pasar el pipeline, el software queda **siempre listo para desplegarse** (artefactos e imágenes construidos y publicados automáticamente), aunque el despliegue a producción se decida manualmente. El **despliegue continuo** va un paso más allá y despliega automáticamente a producción si todas las etapas pasan. En este proyecto aplicamos entrega continua: al hacer push a `main` y pasar las pruebas, las imágenes se publican automáticamente en Docker Hub.

79. **¿Qué es un pipeline y qué etapas puede contener?**
    Un pipeline es la **secuencia automatizada de etapas** que se ejecuta cuando ocurre un evento en el repositorio (push, pull request, etc.). Etapas típicas: instalación de dependencias, ejecución de pruebas, análisis de calidad del código, construcción de las imágenes Docker, autenticación en el registro y publicación o despliegue. Cada etapa depende del éxito de la anterior: si las pruebas fallan, no se publica nada.

80. **¿Qué ventajas ofrece automatizar las pruebas y la construcción de imágenes?**
    Detección temprana de errores, menos trabajo manual y menos errores humanos, entregas más rápidas y confiables, retroalimentación inmediata al equipo y **consistencia de los artefactos**: siempre se construye con el mismo proceso, así que lo que se prueba es exactamente lo que se publica. También libera tiempo del equipo, que deja de repetir tareas mecánicas.

81. **¿Qué función cumplen los secretos y las variables de entorno en un pipeline?**
    Permiten pasar **configuración y credenciales** al pipeline sin escribirlas en el código del repositorio: las variables de entorno llevan datos de configuración (nombres, URLs) y los secretos llevan información sensible (tokens, contraseñas) que la plataforma cifra y **enmascara en los registros**. En este proyecto, `DOCKERHUB_USERNAME` y `DOCKERHUB_TOKEN` se configuran como secretos en GitHub Actions para que el pipeline pueda autenticarse y publicar las imágenes sin exponer credenciales en el repositorio.
