### Filosofía del Diseño

En lugar de una sola tabla gigante, usaremos dos tablas relacionadas. Esto mantiene los datos organizados y es una práctica estándar en el diseño de bases de datos (normalización).

1.  **`sessions` (Sesiones):** Cada vez que se inicia la aplicación, se crea una nueva "sesión". Esta tabla almacenará información general sobre esa sesión de uso, como cuándo comenzó y qué modelo de IA se usó.
2.  **`interactions` (Interacciones):** Esta es la tabla principal. Guardará cada "turno" de la conversación (tanto la entrada del usuario como la respuesta de la IA) y lo vinculará a la sesión correspondiente.

---

### Estructura Detallada de la Base de Datos

#### Tabla 1: `sessions`

Almacena una entrada por cada vez que se ejecuta la aplicación.

| Nombre de la Columna | Tipo de Dato (SQLite)               | Descripción                                                                                       | Ejemplo                     |
| :------------------- | :---------------------------------- | :------------------------------------------------------------------------------------------------ | :-------------------------- |
| **session_id**       | `INTEGER PRIMARY KEY AUTOINCREMENT` | Identificador único para cada sesión de uso.                                                      | `1`                         |
| **start_time**       | `TEXT`                              | Fecha y hora en que comenzó la sesión (formato ISO 8601).                                         | `'2025-08-26T10:30:00Z'`    |
| **end_time**         | `TEXT`                              | Fecha y hora en que terminó la sesión. Puede ser `NULL` si la sesión sigue activa.                | `'2025-08-26T11:15:00Z'`    |
| **model_used**       | `TEXT`                              | Nombre del modelo de IA utilizado en la sesión. Útil para futuras comparaciones.                  | `'Mistral-7B'`              |
| **settings_json**    | `TEXT`                              | Un campo flexible para guardar configuraciones de la sesión en formato JSON (ej. speech timeout). | `'{"speech_timeout": 5.0}'` |

#### Tabla 2: `interactions`

Almacena cada "evento" o "turno" dentro de una sesión. Aquí es donde guardamos los datos ricos para análisis.

| Nombre de la Columna           | Tipo de Dato (SQLite)               | Descripción                                                                                               | Ejemplo                                    |
| :----------------------------- | :---------------------------------- | :-------------------------------------------------------------------------------------------------------- | :----------------------------------------- |
| **interaction_id**             | `INTEGER PRIMARY KEY AUTOINCREMENT` | Identificador único para cada interacción.                                                                | `101`                                      |
| **session_id**                 | `INTEGER`                           | **Clave foránea** que vincula cada interacción con su sesión en la tabla `sessions`.                      | `1`                                        |
| **timestamp**                  | `TEXT`                              | Fecha y hora exacta de la interacción (formato ISO 8601).                                                 | `'2025-08-26T10:32:15Z'`                   |
| **role**                       | `TEXT`                              | Quién es el autor de esta interacción: `'user'` o `'assistant'`. **¡Clave para reconstruir el diálogo!**  | `'user'`                                   |
| **text_content**               | `TEXT`                              | La transcripción del usuario o la respuesta generada por la IA.                                           | `'Me siento muy solo últimamente'`         |
| **facial_emotion_dominant**    | `TEXT`                              | La emoción facial dominante detectada (`NULL` si el rol es 'assistant').                                  | `'sad'`                                    |
| **facial_emotion_scores_json** | `TEXT`                              | El desglose completo de las puntuaciones de emoción en formato JSON. **Mucho más valioso para entrenar.** | `'{"sad": 0.85, "neutral": 0.1, ...}'`     |
| **vocal_analysis_json**        | `TEXT`                              | Un campo JSON para todos los metadatos de voz (emoción, tono, ritmo, etc.). Flexible y escalable.         | `'{"emotion": "sad", "tone": "low", ...}'` |

### Relación entre Tablas

La relación es de "uno a muchos": Una `session` puede tener muchas `interactions`.

```
+--------------+           +--------------------+
|   sessions   |           |    interactions    |
+--------------+           +--------------------+
| session_id   |----------<| session_id         |
| start_time   |           | interaction_id     |
| end_time     |           | timestamp          |
| ...          |           | role               |
+--------------+           | ...                |
                           +--------------------+
```

---

### Código SQL para Crear las Tablas

Este es el código SQL que usaremos en nuestro script de Python para crear la base de datos con esta estructura.

```sql
-- Tabla para registrar cada sesión de uso de la aplicación
CREATE TABLE IF NOT EXISTS sessions (
    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
    start_time TEXT NOT NULL,
    end_time TEXT,
    model_used TEXT,
    settings_json TEXT
);

-- Tabla para registrar cada interacción (turno de usuario o IA) dentro de una sesión
CREATE TABLE IF NOT EXISTS interactions (
    interaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    timestamp TEXT NOT NULL,
    role TEXT NOT NULL, -- 'user' o 'assistant'
    text_content TEXT,
    facial_emotion_dominant TEXT,
    facial_emotion_scores_json TEXT,
    vocal_analysis_json TEXT,
    FOREIGN KEY (session_id) REFERENCES sessions (session_id)
);
```
