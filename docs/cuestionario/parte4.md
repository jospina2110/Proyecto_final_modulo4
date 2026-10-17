# Parte 4. Docker y orquestación — Preguntas teóricas

54. **¿Qué es Docker y cuál es su utilidad en el desarrollo de software?**
    Docker es una plataforma de **contenedores** que permite empaquetar una aplicación junto con todas sus dependencias (librerías, versiones, configuración) en una unidad ligera y portable que se ejecuta igual en cualquier máquina. Su utilidad principal es eliminar el problema de "en mi máquina funciona": garantiza entornos reproducibles, aísla las aplicaciones entre sí, acelera el despliegue y encaja perfecto con pipelines de CI/CD como el de este proyecto.

55. **¿Cuál es la diferencia entre una imagen y un contenedor?**
    Una **imagen** es una plantilla de solo lectura construida por capas (sistema base, dependencias, código); es el "molde". Un **contenedor** es una **instancia en ejecución** de esa imagen, con su propio proceso y su capa de escritura. La relación es como la de una clase y sus objetos: de una misma imagen se pueden crear muchos contenedores. Ejemplo del proyecto: la imagen `medical-appointments-backend:v1.0` y el contenedor que la ejecuta con uvicorn.

56. **¿Qué función cumple un Dockerfile?**
    Es el **archivo de instrucciones para construir una imagen**: define la imagen base (`FROM`), copia archivos (`COPY`), ejecuta comandos de instalación (`RUN`), documenta el puerto (`EXPOSE`) y define el proceso de arranque (`CMD`). En el proyecto, `backend/Dockerfile` instala los `requirements.txt` y arranca uvicorn; `frontend/Dockerfile` copia el sitio dentro de una imagen de nginx.

57. **¿Qué es Docker Compose y qué problema soluciona?**
    Es una herramienta para **definir y ejecutar aplicaciones con varios contenedores** desde un solo archivo YAML, donde se declaran los servicios, las redes y los volúmenes. Soluciona el tener que levantar cada contenedor por separado con `docker run`, conectarlos a mano y recordar todos sus parámetros: con `docker compose up` se levanta la aplicación completa (mongo + backend + frontend) de forma ordenada y repetible.

58. **¿Qué función cumplen los volúmenes de Docker?**
    Sirven para **persistir datos fuera del ciclo de vida del contenedor**. Un contenedor puede destruirse y recrearse, pero la información guardada en un volumen se conserva. En este proyecto el volumen `mongo_data` almacena el directorio `/data/db` de MongoDB, de modo que los pacientes, médicos y citas no se pierden al reiniciar o reconstruir los servicios.

59. **¿Qué diferencia existe entre exponer un puerto y publicar un puerto?**
    **Exponer** un puerto (`EXPOSE`) solo lo documenta: indica que el proceso escucha en ese puerto dentro de la red interna de contenedores, pero no lo hace accesible desde fuera. **Publicar** un puerto (`ports: "8080:80"`) crea un mapeo entre un puerto del computador anfitrión y el del contenedor, permitiendo el acceso desde el exterior. En el proyecto, el backend solo **expone** el 8000 (se consume dentro de la red de Compose) y el frontend **publica** el `8080:80` para entrar desde el navegador.

60. **¿Qué ventajas ofrece ejecutar una aplicación dentro de contenedores frente a ejecutarla directamente en el sistema operativo?**
    Portabilidad y reproducibilidad (el mismo entorno en cualquier máquina), aislamiento de dependencias (dos proyectos pueden usar versiones distintas sin chocar), despliegue rápido y consistente, arranque ligero comparado con una máquina virtual, facilidad para escalar horizontalmente y una integración natural con CI/CD. Ejecutar directamente en el sistema operativo obliga a instalar y configurar versiones a mano en cada máquina, con riesgo de conflictos.
