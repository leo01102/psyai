# tests/unit/test_database.py

import sys
import os
from pathlib import Path
REPO_ROOT = Path(os.path.dirname(os.path.abspath(__file__))).parents[1]
sys.path.insert(0, str(REPO_ROOT))

import pytest
import sqlite3
from src.database.data_manager import create_connection, setup_database, save_interaction_encrypted, CipherManager

from cryptography.fernet import Fernet

# --- Fixtures ---
@pytest.fixture
def db_connection():
    """Base de datos en memoria para pruebas unitarias."""
    conn = sqlite3.connect(":memory:")
    setup_database(conn)
    yield conn
    conn.close()

@pytest.fixture
def test_cipher():
    """Clave de cifrado de prueba."""
    key = Fernet.generate_key().decode()
    return CipherManager(key)

# --- Tests ---
def test_save_and_read_encrypted_interaction(db_connection, test_cipher):
    from src.database import data_manager
    data_manager.cipher = test_cipher  # Sobrescribimos el cipher global para la prueba

    # Datos de prueba
    session_id = 1
    role = 'user'
    original_text = "Este es un mensaje secreto de prueba."
    data = {"text": original_text, "facial_dominant": "happy"}

    # Guardar datos cifrados
    save_interaction_encrypted(db_connection, session_id, role, data)

    # Leer directamente de la BD para verificar
    cursor = db_connection.cursor()
    cursor.execute("SELECT text_content FROM interactions WHERE interaction_id=1")
    row = cursor.fetchone()
    
    assert row is not None
    encrypted_text = row[0]

    # Verificar que no es texto plano
    assert encrypted_text != original_text
    
    # Verificar que se puede descifrar correctamente
    decrypted_text = test_cipher.decrypt(encrypted_text)
    assert decrypted_text == original_text
