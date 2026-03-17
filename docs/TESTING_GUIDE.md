# Guía de Pruebas

Este documento describe los procedimientos para verificar la estabilidad y el correcto funcionamiento de la plataforma.

## Pruebas Automatizadas

Las pruebas automatizadas se encuentran en el directorio `tests/` y utilizan el framework `pytest`.

### Ejecución de Pruebas

Para ejecutar todas las pruebas automatizadas, sigue estos pasos:

1.  Navega a la raíz del proyecto.
2.  Activa el entorno virtual del backend.
3.  Ejecuta el lanzador de pruebas:

```bash
cd APP/backend
pytest ../tests/
```

### Resumen del Conjunto de Pruebas

- `test_auth_system.py`: Verifica el registro de usuarios, inicio de sesión, actualización de tokens y acceso a rutas protegidas.
- `test_video_crud.py`: Asegura que los videos puedan ser creados, listados, recuperados y eliminados.
- `test_video_pipeline.py`: Prueba las transiciones de estado completas de la tubería desde QUEUED hasta DONE.
- `test_download_endpoint.py`: Confirma que los enlaces de descarga solo están disponibles para videos completados.
- `test_video_ownership.py`: Valida que los usuarios no puedan acceder a los videos de otros usuarios.
- `test_pagination.py`: Prueba la lógica de límite y desplazamiento (offset) de la lista de videos.
- `e2e_test_flow.py`: Un script que simula el recorrido completo de un usuario a través de la plataforma.

---

## Procedimientos de Verificación Manual

Sigue estos pasos para verificar manualmente la funcionalidad principal de la plataforma.

### 1. Incorporación de Usuarios (Onboarding)

1.  Abre la aplicación en un navegador.
2.  Haz clic en **Registrarse** (Register) y crea una nueva cuenta.
3.  Verifica que eres redirigido automáticamente a la página de **Inicio de sesión** (Login) o al **Panel de Control** (Dashboard).
4.  Cierra sesión y vuelve a iniciarla para asegurar la persistencia de la sesión.

### 2. Creación y Progreso de Videos

1.  Desde el Panel de Control, haz clic en **Crear Nuevo Video** (Create New Video).
2.  Rellena los detalles de la plantilla y haz clic en **Generar** (Generate).
3.  Observa la lista de videos:
    - El nuevo video debería aparecer con el estado `QUEUED`.
    - En unos segundos, el estado debería cambiar a `PROCESSING` (mostrando los pasos específicos de la tubería).
    - Verifica que la barra de progreso o los indicadores de estado se actualicen en tiempo real.

### 3. Verificación de Archivos

1.  Espera hasta que el estado del video sea `DONE`.
2.  Haz clic en el botón de **Descargar** (Download).
3.  Verifica que el archivo de video se descarga correctamente y se puede reproducir.
4.  Navega al directorio `APP/backend/videos/` y asegúrate de que el archivo existe en la subcarpeta correcta del usuario.

### 4. Seguridad y Separación

1.  Abre una ventana de Incógnito/Privada.
2.  Inicia sesión con una cuenta **diferente**.
3.  Verifica que la lista de videos esté vacía o no muestre los videos de la primera cuenta.
4.  Intenta acceder manualmente a un ID de video de la primera cuenta a través de la URL (si corresponde) y verifica que devuelva un error 404 o acceso denegado.

### 5. Paginación

1.  Crea más de 20 videos (o el límite actual de la página).
2.  Verifica que los controles de paginación aparezcan en la parte inferior de la lista.
3.  Haz clic a través de las páginas y asegúrate de que se muestran diferentes videos.
