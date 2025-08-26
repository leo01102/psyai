# src/database/data_manager.py | Funciones para inicializar la DB, guardar y consultar registros

import sqlite3
from sqlite3 import Error
import os
import json
from datetime import datetime

DB_FILE = os.path.join("data", "psyai.db")

def create_connection():
    """Crea una conexión a la base de datos SQLite."""
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
    except Error as e:
        print(f"Error al conectar con la base de datos: {e}")
    return conn

def setup_database(conn):
    """Ejecuta los comandos SQL para crear las tablas si no existen."""
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
    try:
        cursor = conn.cursor()
        cursor.execute(sql_create_sessions_table)
        cursor.execute(sql_create_interactions_table)
        conn.commit()
    except Error as e:
        print(f"Error al crear las tablas: {e}")

def start_new_session(conn, model_used="Mistral-7B", settings=None):
    """Inicia una nueva sesión y devuelve el ID de la sesión."""
    sql = '''INSERT INTO sessions(start_time, model_used, settings_json)
             VALUES(?,?,?)'''
    try:
        cursor = conn.cursor()
        start_time = datetime.now().isoformat()
        settings_str = json.dumps(settings) if settings else None
        cursor.execute(sql, (start_time, model_used, settings_str))
        conn.commit()
        return cursor.lastrowid  # Devuelve el ID de la nueva sesión
    except Error as e:
        print(f"Error al iniciar una nueva sesión: {e}")
        return None

def save_interaction(conn, session_id, role, data):
    """
    Guarda una interacción (de usuario o asistente) en la base de datos.
    'data' es un diccionario que contiene la información del turno.
    """
    sql = '''INSERT INTO interactions(session_id, timestamp, role, text_content, 
                                      facial_emotion_dominant, facial_emotion_scores_json, vocal_analysis_json)
             VALUES(?,?,?,?,?,?,?)'''
    try:
        cursor = conn.cursor()
        timestamp = data.get("timestamp", datetime.now().isoformat())
        
        # Convertir diccionarios a strings JSON para almacenar
        scores_json = json.dumps(data.get("facial_scores")) if data.get("facial_scores") else None
        vocal_json = json.dumps(data.get("vocal_analysis")) if data.get("vocal_analysis") else None

        data_tuple = (
            session_id,
            timestamp,
            role,
            data.get("text"),
            data.get("facial_dominant"),
            scores_json,
            vocal_json
        )
        cursor.execute(sql, data_tuple)
        conn.commit()
        return cursor.lastrowid
    except Error as e:
        print(f"Error al guardar la interacción: {e}")
        return None