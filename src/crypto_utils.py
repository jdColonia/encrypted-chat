import base64
import hashlib
import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    ParameterFormat,
    PublicFormat,
    load_pem_parameters,
    load_pem_public_key,
)


class CryptoManager:
    def __init__(self):
        self.dh_private_key = None
        self.dh_public_key = None
        self.shared_key = None
        self.dh_parameters = None

    def generate_dh_parameters(self):
        """Genera parámetros Diffie-Hellman (p, g)"""
        print("🔄 Generando parámetros Diffie-Hellman...")
        self.dh_parameters = dh.generate_parameters(
            generator=2, key_size=2048, backend=default_backend()
        )
        print("✅ Parámetros Diffie-Hellman generados")

    def load_dh_parameters(self, parameters_pem):
        """Carga parámetros DH desde formato PEM"""
        self.dh_parameters = load_pem_parameters(
            parameters_pem, backend=default_backend()
        )
        print("✅ Parámetros Diffie-Hellman cargados")

    def get_dh_parameters_pem(self):
        """Retorna parámetros DH en formato PEM"""
        return self.dh_parameters.parameter_bytes(
            encoding=Encoding.PEM, format=ParameterFormat.PKCS3
        )

    def generate_dh_keypair(self):
        """Genera par de llaves Diffie-Hellman"""
        if not self.dh_parameters:
            raise ValueError("Parámetros DH no inicializados")

        self.dh_private_key = self.dh_parameters.generate_private_key()
        self.dh_public_key = self.dh_private_key.public_key()
        print("✅ Par de llaves Diffie-Hellman generado")

    def get_dh_public_key_bytes(self):
        """Retorna la llave pública DH en formato de bytes"""
        return self.dh_public_key.public_bytes(
            encoding=Encoding.PEM, format=PublicFormat.SubjectPublicKeyInfo
        )

    def compute_shared_key(self, peer_public_key_bytes):
        """Computa la clave compartida usando la llave pública del peer"""
        # Cargar llave pública del peer
        peer_public_key = load_pem_public_key(
            peer_public_key_bytes, backend=default_backend()
        )

        # Computar secreto compartido
        shared_secret = self.dh_private_key.exchange(peer_public_key)

        # Derivar clave AES-256 (32 bytes) usando HKDF
        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32, # 256 bits
            salt=None,
            info=b"chat-encryption-key",
            backend=default_backend(),
        ).derive(shared_secret)

        self.shared_key = derived_key

        # Mostrar fingerprint de la clave compartida (para verificación)
        key_fingerprint = hashlib.sha256(derived_key).hexdigest()[:16]
        print(f"🔑 Clave compartida AES-256 establecida")
        print(f"🔍 Fingerprint de sesión: {key_fingerprint}")

        return derived_key

    def encrypt_message(self, message):
        """Cifra mensaje usando AES-256-GCM"""
        if not self.shared_key:
            raise ValueError("Clave compartida no establecida")

        # Generar IV aleatorio (12 bytes para GCM)
        iv = os.urandom(12)

        # Crear cifrador AES-GCM
        cipher = Cipher(
            algorithms.AES(self.shared_key), modes.GCM(iv), backend=default_backend()
        )
        encryptor = cipher.encryptor()

        # Cifrar mensaje
        message_bytes = message.encode("utf-8")
        ciphertext = encryptor.update(message_bytes) + encryptor.finalize()

        # Obtener tag de autenticación
        tag = encryptor.tag

        # Concatenar: IV + TAG + CIPHERTEXT y codificar en base64
        encrypted_data = iv + tag + ciphertext
        return base64.b64encode(encrypted_data).decode("utf-8")

    def decrypt_message(self, encrypted_message):
        """Descifra mensaje usando AES-256-GCM"""
        if not self.shared_key:
            raise ValueError("Clave compartida no establecida")

        # Decodificar base64
        encrypted_data = base64.b64decode(encrypted_message.encode("utf-8"))

        # Extraer IV (12 bytes), TAG (16 bytes), y CIPHERTEXT
        iv = encrypted_data[:12]
        tag = encrypted_data[12:28]
        ciphertext = encrypted_data[28:]

        # Crear descifrador AES-GCM
        cipher = Cipher(
            algorithms.AES(self.shared_key),
            modes.GCM(iv, tag),
            backend=default_backend(),
        )
        decryptor = cipher.decryptor()

        # Descifrar mensaje
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        return plaintext.decode("utf-8")

    def get_shared_key_fingerprint(self):
        """Retorna el fingerprint de la clave compartida para verificación"""
        if not self.shared_key:
            return None
        fingerprint = hashlib.sha256(self.shared_key).hexdigest()
        return ":".join(fingerprint[i : i + 2] for i in range(0, len(fingerprint), 2))
