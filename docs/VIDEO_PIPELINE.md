# Tubería de Video (Video Pipeline)

## Descripción General

El proceso de generación de video se orquesta como una serie de pasos discretos e idempotentes ejecutados por los workers de Celery. Esto garantiza la fiabilidad y permite al sistema recuperarse de fallos sin reiniciar todo el proceso.

## Pasos de la Tubería

La tubería sigue un orden estricto:

1.  **QUEUED**: Estado inicial cuando el trabajo se añade a la cola de Redis.
2.  **SCRIPTING**: Genera el guion de texto y las escenas utilizando IA.
3.  **SCRIPT_VALIDATED**: Asegura que el guion generado cumpla con los estándares de calidad y seguridad.
4.  **IMAGE_GENERATION**: Crea activos visuales para cada escena utilizando generadores de imágenes por IA.
5.  **VOICE_SYNTHESIS**: Genera la narración de audio para cada escena utilizando Texto-a-Voz (TTS).
6.  **MEDIA_COMPOSITION**: Combina los activos visuales y de audio en un flujo (stream) de video en bruto.
7.  **ENCODING**: Finaliza el archivo de video utilizando FFmpeg (optimización de la tasa de bits, metadatos).
8.  **UPLOADING**: Mueve el archivo final al almacenamiento designado (Local o en la Nube).
9.  **DONE**: El video está listo para su descarga y el estado finalizado.

## Orquestación Fiable

### Seguimiento del VideoJob

Cada ejecución de un paso se registra en la tabla `VideoJob`. Este registro incluye:

- Nombre del paso.
- Marcas de tiempo (timestamps) de inicio y fin.
- Estado de Éxito/Fallo.
- Mensajes de error (si corresponde).

### Idempotencia

Antes de iniciar un paso, el orquestador comprueba si ese paso específico ya ha sido marcado como éxito (`success`) en la tabla `VideoJob` para el `video_id` actual. Si es así, se omite el paso. Esto permite que el flujo de trabajo se vuelva a ejecutar de forma segura varias veces.

### Recuperación de Fallos (Crash Recovery)

Si un worker falla en mitad de una tarea:

1.  La entrada `VideoJob` para el paso activo permanece sin una marca de tiempo de fin (`ended_at`).
2.  El estado del `GeneratedVideo` permanece en el último paso intentado.
3.  Al reiniciar o reintentar, el orquestador utiliza `get_resume_index()` para encontrar el primer paso incompleto y se reanuda desde allí.

### Lógica de Reintento

- Los pasos fallidos se capturan y se incrementa el contador de reintentos (`retry_count`) del video.
- El sistema reintenta automáticamente el flujo de trabajo utilizando un retroceso exponencial (ej., 60 segundos).
- Un video se marca como `FAILED` (fallido) solo después de alcanzar el número máximo de reintentos (actualmente 3).
