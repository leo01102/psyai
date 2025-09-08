### Filosofía del Diseño

Se utiliza un diseño de base de datos normalizado con tres tablas principales para separar las preocupaciones y mantener los datos organizados:

1.  **`sessions`**: Registra cada ejecución de la aplicación.
2.  **`interactions`**: Almacena cada turno de la conversación (usuario y asistente) dentro de una sesión.
3.  **`user_memory`**: Guarda hechos clave extraídos sobre el usuario para crear una memoria a largo plazo, independiente de las sesiones.

---

### Estructura Detallada de la Base de Datos

#### Tabla 1: `sessions`

Almacena metadatos de alto nivel sobre cada sesión de uso.

| Nombre de la Columna | Tipo de Dato (SQLite) | Descripción |
| :--- | :--- | :--- |
| **session_id** | `INTEGER PRIMARY KEY AUTOINCREMENT` | Identificador único para la sesión. |
| **start_time** | `TEXT` | Fecha y hora de inicio de la sesión (formato ISO 8601). |
| **end_time** | `TEXT` | Fecha y hora de finalización (NULL si está activa). |
| **model_used** | `TEXT` | Nombre del modelo de IA utilizado. |
| **settings_json** | `TEXT` | Configuraciones de la sesión en formato JSON. |

#### Tabla 2: `interactions`

Almacena cada mensaje intercambiado durante una sesión.

| Nombre de la Columna | Tipo de Dato (SQLite) | Descripción |
| :--- | :--- | :--- |
| **interaction_id** | `INTEGER PRIMARY KEY AUTOINCREMENT` | Identificador único para la interacción. |
| **session_id** | `INTEGER` | Clave foránea que la vincula a la tabla `sessions`. |
| **timestamp** | `TEXT` | Fecha y hora exacta de la interacción. |
| **role** | `TEXT` | Autor del mensaje: `'user'` o `'assistant'`. |
| **text_content** | `TEXT` | **(Cifrado)** Transcripción o respuesta de la IA. |
| **facial_emotion_dominant** | `TEXT` | Emoción facial dominante estable detectada. |
| **facial_emotion_scores_json** | `TEXT` | Desglose de puntuaciones de emoción promedio en formato JSON. |
| **vocal_analysis_json** | `TEXT` | **(En uso)** Resultados del análisis de emoción vocal (lista de emociones y scores) en formato JSON. |

#### Tabla 3: `user_memory`

Almacena hechos clave sobre el usuario para la memoria a largo plazo.

| Nombre de la Columna | Tipo de Dato (SQLite) | Descripción |
| :--- | :--- | :--- |
| **key** | `TEXT PRIMARY KEY` | La clave del hecho (ej. 'nombre', 'tema_recurrente'). |
| **value** | `TEXT` | **(Cifrado)** El valor del hecho extraído por la IA. |
| **last_updated** | `TEXT` | Fecha y hora de la última actualización de este hecho. |

---

### Relación entre Tablas

El diagrama muestra que una `session` puede tener muchas `interactions`. La tabla `user_memory` es independiente, actuando como un perfil de usuario persistente.

```
+--------------+          +--------------------+
|   sessions   |          |    interactions    |
+--------------+          +--------------------+
| session_id   |---------<| session_id         |
| start_time   |          | interaction_id     |
| end_time     |          | timestamp          |
| ...          |          | role               |
+--------------+          | ...                |
                          +--------------------+

+----------------+
|  user_memory   |
+----------------+
| key            |
| value          |
| last_updated   |
+----------------+
```

---

### Código SQL para la Creación del Esquema

Este es el código SQL de referencia, tal como se implementa en `src/database/data_manager.py`, para crear la estructura completa de la base de datos.

```sql
-- Tabla para registrar cada sesión de uso de la aplicación
CREATE TABLE IF NOT EXISTS sessions (
    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
    start_time TEXT NOT NULL,
    end_time TEXT,
    model_used TEXT,
    settings_json TEXT
);

-- Tabla para registrar cada interacción dentro de una sesión
CREATE TABLE IF NOT EXISTS interactions (
    interaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    timestamp TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
    text_content TEXT,
    facial_emotion_dominant TEXT,
    facial_emotion_scores_json TEXT,
    vocal_analysis_json TEXT,
    FOREIGN KEY (session_id) REFERENCES sessions (session_id)
);

-- Tabla para la memoria a largo plazo del usuario
CREATE TABLE IF NOT EXISTS user_memory (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    last_updated TEXT NOT NULL
);
```

---

### Seguridad y Cifrado

Para proteger la privacidad del usuario, los campos de texto sensibles se cifran antes de ser guardados en la base de datos.

-   **Campos Cifrados:** `interactions.text_content` y `user_memory.value`.
-   **Algoritmo:** Se utiliza un cifrado simétrico robusto (AES con modo GCM) a través de la librería `cryptography` de Python.
-   **Gestión de la Clave:** La clave de cifrado (`ENCRYPTION_KEY`) se genera localmente usando `scripts/generate_key.py` y se almacena en el archivo `.env`. **Es crucial no subir este archivo a repositorios públicos.** La lógica de cifrado y descifrado está centralizada en el módulo `src/database/data_manager.py`.
