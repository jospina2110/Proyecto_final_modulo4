# Parte 2. Arquitectura de software y API REST — Preguntas teóricas

23. **¿Qué es una arquitectura de software?**
    Es el conjunto de **decisiones estructurales** que definen cómo se organiza un sistema: qué componentes tiene, qué responsabilidad cumple cada uno y cómo se comunican entre sí. No es el código en sí, sino el "plano" que guía cómo se construye. En este proyecto, la arquitectura es **por capas**: `routes` (HTTP) → `services` (negocio) → `repositories` (datos) → `models` (documentos).

24. **Explique qué caracteriza a una arquitectura monolítica.**
    Se caracteriza porque **toda la aplicación se desarrolla, empaqueta y despliega como una sola unidad**: un único proceso y un único artefacto. Esto simplifica el desarrollo, las pruebas y el despliegue al principio, pero si el sistema crece mucho se vuelve difícil de escalar por partes y un fallo puede afectar a todo. Nuestro backend es un monolito (una sola aplicación FastAPI) con **separación interna por capas**, lo que mantiene el orden sin la complejidad de los microservicios.

25. **¿Qué es una arquitectura de microservicios?**
    Es un estilo en el que la aplicación se divide en **servicios pequeños e independientes**, cada uno con una responsabilidad concreta, su propio despliegue y su propia base de datos si hace falta, comunicándose por la red (HTTP, mensajería). Por ejemplo, se podría separar un servicio de citas, uno de pacientes y uno de notificaciones. Cada servicio puede escalar y desplegarse por separado.

26. **Mencione dos ventajas y dos desventajas de los microservicios.**
    **Ventajas:** (1) cada servicio puede escalarse y desplegarse de forma independiente según su demanda; (2) permiten autonomía de equipos e incluso usar tecnologías distintas por servicio. **Desventajas:** (1) la complejidad operativa aumenta mucho (muchos despliegues, monitoreo, configuración de red); (2) la consistencia de datos y la depuración de errores se complican porque una operación puede atravesar varios servicios.

27. **¿Qué es una API REST y cuáles son sus principales características?**
    Una API REST es una interfaz que expone **recursos** identificados por URLs y se opera con los **verbos HTTP** (GET, POST, PATCH, DELETE), intercambiando representaciones como JSON. Sus características principales son: modelo cliente-servidor, **sin estado** (cada petición incluye todo lo necesario, el servidor no recuerda al cliente), interfaz uniforme, respuestas cacheables y uso de **códigos de estado HTTP** para comunicar el resultado. En el proyecto: `POST /patients` registra, `GET /appointments` consulta, `DELETE /appointments/{id}` cancela.

28. **¿Qué responsabilidad tiene un controlador dentro de una aplicación backend?**
    El controlador es la **capa de entrada HTTP**: recibe la petición, valida el formato de los datos de entrada, delega la lógica en el servicio correspondiente y construye la respuesta con el código de estado adecuado. **No debería contener reglas de negocio**. En nuestro proyecto son los archivos de `app/routes/`, por ejemplo `patients.py` con las funciones `register_patient` y `list_patients`.

29. **¿Qué responsabilidad tiene un servicio?**
    El servicio contiene las **reglas de negocio** de la aplicación: decide qué está permitido, coordina las operaciones y llama a la capa de acceso a datos. Tampoco sabe nada de HTTP. Ejemplo real del proyecto: `appointment_service.py` verifica que el paciente y el médico existan y que el médico no tenga una cita que se solape en el horario antes de guardar la nueva cita.

30. **¿Qué función cumple la capa de acceso a datos?**
    Es la capa que **abstrae y centraliza las consultas a la base de datos**: insertar, buscar, filtrar y actualizar documentos. Al ser la única capa que habla con MongoDB, permite cambiar la tecnología de persistencia sin tocar la lógica de negocio, facilita las pruebas y evita repetir consultas por todo el código. En el proyecto está en `app/repositories/`, usando Beanie.

31. **¿Qué es una arquitectura por capas y qué ventajas ofrece?**
    Es una forma de organizar la aplicación en **niveles jerárquicos donde cada capa solo utiliza la inmediatamente inferior**: entrada HTTP → lógica de negocio → acceso a datos. Ventajas: separación de responsabilidades, código más fácil de mantener y entender, componentes reutilizables, pruebas más sencillas (cada capa se puede probar por separado) y cambios localizados: si cambia la base de datos, solo se toca la capa de acceso a datos.

32. **¿Qué criterios deben considerarse para seleccionar la arquitectura de una aplicación?**
    Se deben considerar: el **tamaño y la complejidad** del sistema, los requisitos de **escalabilidad y disponibilidad**, el **tiempo y presupuesto** del proyecto, el **tamaño y experiencia del equipo**, la **frecuencia de cambios** prevista y los requisitos de despliegue. La recomendación general es empezar por la arquitectura **más simple que cumpla los requisitos** (por ejemplo, un monolito por capas como el de este proyecto) y evolucionar solo si hace falta.
