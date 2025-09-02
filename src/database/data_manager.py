# src/database/data_manager.py | Funciones para inicializar la DB, guardar y consultar registros

import sqlite3
from sqlite3 import Error
import os
import json
from datetime import datetime
from cryptography.fernet import Fernet
import config

# --- GESTIÓN DE CIFRADO ---
# Documentación Clave: La clave de cifrado se carga desde ENCRYPTION_KEY en el .env.
# Para rotar la clave:
# 1. Genere una nueva clave con `Fernet.generate_key().decode()`.
# 2. Actualice la variable ENCRYPTION_KEY en .env.
# 3. Se necesitará una estrategia de migración para descifrar los datos antiguos con la clave
#    vieja y volver a cifrarlos con la nueva.
class CipherManager:
    def __init__(self, key: str):
        if not key:
            raise ValueError("La clave de cifrado no puede estar vacía.")
        self.cipher = Fernet(key.encode())

    def encrypt(self, plaintext: str) -> str:
        if not plaintext:
            return plaintext
        return self.cipher.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        if not ciphertext:
            return ciphertext
        return self.cipher.decrypt(ciphertext.encode()).decode()

cipher = CipherManager(config.ENCRYPTION_KEY)
DB_FILE = os.path.join("data", "psyai.db")

def create_connection():
    """Crea una conexión a la base de datos SQLite."""
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    conn = None
    try:
        # check_same_thread=False es necesario para que Streamlit funcione correctamente
        # con la base de datos en su modelo de ejecución.
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    except Error as e:
        print(f"Error al conectar con la base de datos: {e}")
    return conn

def setup_database():
    """Crea todas las tablas necesarias si no existen. Maneja su propia conexión."""
    conn = create_connection()
    if conn is None:
        print("Error: No se pudo crear la conexión a la base de datos.")
        return

    sql_create_sessions_table = """
    CREATE TABLE IF NOT EXISTS sessions (
        session_id INTEGER PRIMARY KEY AUTOINCREMENT,
        start_time TEXT NOT NULL,
        end_time TEXT,
        model_used TEXT,
        settings_json TEXT
    );
    """
    sql_create_interactions_table = """
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
    """
    sql_create_memory_table = """
    CREATE TABLE IF NOT EXISTS user_memory (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        last_updated TEXT NOT NULL
    );
    """
    
    try:
        cursor = conn.cursor()
        cursor.execute(sql_create_sessions_table)
        cursor.execute(sql_create_interactions_table)
        cursor.execute(sql_create_memory_table)
        conn.commit()
    except Error as e:
        print(f"Error al crear las tablas: {e}")
    finally:
        if conn:
            conn.close()

def start_new_session(model_used="llama-3.1-8b-instant", settings=None):
    """Inicia una nueva sesión y devuelve su ID. Maneja su propia conexión."""
    conn = create_connection()
    if conn is None: return None
    
    sql = '''INSERT INTO sessions(start_time, model_used, settings_json)
             VALUES(?,?,?)'''
    session_id = None
    try:
        cursor = conn.cursor()
        start_time = datetime.now().isoformat()
        settings_str = json.dumps(settings) if settings else None
        cursor.execute(sql, (start_time, model_used, settings_str))
        conn.commit()
        session_id = cursor.lastrowid
    except Error as e:
        print(f"Error al iniciar una nueva sesión: {e}")
    finally:
        if conn:
            conn.close()
    return session_id

def _save_interaction_internal(conn, session_id, role, data):
    """Función interna para guardar una interacción. Reutiliza una conexión."""
    sql = '''INSERT INTO interactions(session_id, timestamp, role, text_content, 
                                      facial_emotion_dominant, facial_emotion_scores_json, vocal_analysis_json)
             VALUES(?,?,?,?,?,?,?)'''
    try:
        cursor = conn.cursor()
        timestamp = data.get("timestamp", datetime.now().isoformat())
        scores_json = json.dumps(data.get("facial_scores")) if data.get("facial_scores") else None
        vocal_json = json.dumps(data.get("vocal_analysis")) if data.get("vocal_analysis") else None
        
        data_tuple = (
            session_id, timestamp, role, data.get("text"),
            data.get("facial_dominant"), scores_json, vocal_json
        )
        cursor.execute(sql, data_tuple)
        conn.commit()
        return cursor.lastrowid
    except Error as e:
        print(f"Error al guardar la interacción: {e}")
        return None

def save_interaction_encrypted(session_id, role, data):
    """Cifra los datos sensibles y los guarda. Maneja su propia conexión."""
    conn = create_connection()
    if conn is None: return None
    
    interaction_id = None
    try:
        encrypted_data = data.copy()
        if 'text' in encrypted_data and encrypted_data['text']:
            encrypted_data['text'] = cipher.encrypt(encrypted_data['text'])
        
        db_payload = {
            "text": encrypted_data.get("text"),
            "facial_dominant": data.get("facial_dominant"),
            "facial_scores": data.get("facial_scores"),
            "vocal_analysis": data.get("vocal_analysis")
        }
        interaction_id = _save_interaction_internal(conn, session_id, role, db_payload)
    finally:
        if conn:
            conn.close()
    return interaction_id

def save_memory_fact(key: str, value):
    """Guarda o actualiza un hecho en memoria. Maneja su propia conexión."""
    conn = create_connection()
    if conn is None: return
    
    # Asegura que el valor sea siempre un string antes de cifrar
    value_str = str(value)
    
    sql = '''INSERT OR REPLACE INTO user_memory(key, value, last_updated)
             VALUES(?,?,?)'''
    try:
        encrypted_value = cipher.encrypt(value_str)
        cursor = conn.cursor()
        cursor.execute(sql, (key, encrypted_value, datetime.now().isoformat()))
        conn.commit()
    except Error as e:
        print(f"Error al guardar en memoria: {e}")
    finally:
        if conn:
            conn.close()

def get_all_memory():
    """Recupera toda la memoria y la descifra. Maneja su propia conexión."""
    conn = create_connection()
    if conn is None: return {}

    memories = {}
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM user_memory")
        rows = cursor.fetchall()
        for row in rows:
            memories[row[0]] = cipher.decrypt(row[1])
    except Error as e:
        print(f"Error al recuperar memoria: {e}")
    finally:
        if conn:
            conn.close()
    return memories
