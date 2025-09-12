# backend/scripts/generate_key.py | Generate your key for ENCRYPTION_KEY

from cryptography.fernet import Fernet

# Genera una clave nueva y segura
key = Fernet.generate_key()

# La clave está en bytes, la convertimos a string para poder pegarla en el .env
key_str = key.decode()

print("¡Tu nueva clave de cifrado está lista!")
print("Copia la siguiente línea completa y pégala en tu archivo .env:")
print("-" * 50)
print(f"ENCRYPTION_KEY={key_str}")
print("-" * 50)
