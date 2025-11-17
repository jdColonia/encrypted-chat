import socket
import threading
import json
import time
from datetime import datetime
from crypto_utils import CryptoManager


class SecureChatClient:
    def __init__(self, username):
        self.username = username
        self.crypto = CryptoManager()
        self.socket = None
        self.connected = False
        self.peer_username = None
        self.key_established = False

    def connect(self, host="localhost", port=8888):
        self.key_established = False
        self.peer_username = None
        self.crypto.shared_key = None
        
        """Conecta al servidor y registra el usuario"""
        try:
            # Conectar al servidor
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))

            # Registrar usuario
            register_data = {"username": self.username}
            self.socket.send((json.dumps(register_data) + "\n").encode("utf-8"))

            # Establecer conexión
            self.connected = True

            # Iniciar thread para recibir mensajes
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()

            print(f"✅ Conectado al servidor como {self.username}")
            print("⏳ Esperando a otro usuario para iniciar negociación Diffie-Hellman...")

        except Exception as e:
            print(f"❌ Error de conexión: {e}")

    def receive_messages(self):
        """Thread para recibir mensajes del servidor"""
        buffer = ""
        while self.connected:
            try:
                data = self.socket.recv(8192).decode("utf-8")
                if not data:
                    print("⚠ Conexión cerrada por el servidor")
                    self.connected = False
                    return


                buffer += data
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if line.strip():
                        message = json.loads(line)
                        self.handle_received_message(message)

            except Exception as e:
                if self.connected:
                    print(f"❌ Error recibiendo mensaje: {e}")
                break

    def handle_received_message(self, message):
        """Maneja mensajes recibidos del servidor"""
        msg_type = message.get("type")

        if msg_type == "registration_success":
            print(f"🎉 {message['message']}")

        elif msg_type == "dh_parameters":
            print("\n🔐 Negociación Diffie-Hellman...")
            parameters_pem = message["parameters"].encode("utf-8")
            self.crypto.load_dh_parameters(parameters_pem)

            # Generar nuestro par de llaves
            self.crypto.generate_dh_keypair()

            # Enviar llave pública DH al servidor
            dh_exchange_msg = {
                "type": "dh_public_key",
                "public_key": self.crypto.get_dh_public_key_bytes().decode("utf-8"),
            }
            self.socket.send((json.dumps(dh_exchange_msg) + "\n").encode("utf-8"))
            print("   → Llave pública enviada")

        elif msg_type == "dh_peer_public_key":
            # Recibir llave pública del peer y computar clave compartida
            self.peer_username = message["from"]
            peer_public_key = message["public_key"].encode("utf-8")

            # Computar clave compartida
            self.crypto.compute_shared_key(peer_public_key)
            self.key_established = True
            
            print(f"   ✅ Negociación completada con {self.peer_username}")
            print("   🔒 Canal seguro establecido con AES-256-GCM\n")

        elif msg_type == "encrypted_message":
            # Descifrar mensaje
            try:
                # Obtener información del mensaje
                sender = message["from"]
                encrypted_content = message["encrypted_content"]
                timestamp = datetime.fromtimestamp(message["timestamp"])

                # Descifrar mensaje
                if not self.key_established:
                    print("⚠ Mensaje recibido antes de establecer clave, ignorando")
                    return

                decrypted_message = self.crypto.decrypt_message(encrypted_content)

                print(f"[{timestamp.strftime('%H:%M:%S')}] {sender}: {decrypted_message}")

            except Exception as e:
                print(f"❌ Error descifrando mensaje: {e}")

    def send_message(self, message):
        """Envía mensaje cifrado"""
        if not self.key_established:
            print("❌ No se puede enviar mensaje: clave compartida no establecida")
            return

        try:
            # Cifrar mensaje
            encrypted_content = self.crypto.encrypt_message(message)

            # Enviar al servidor
            message_data = {
                "type": "chat_message",
                "encrypted_content": encrypted_content,
            }
            self.socket.send((json.dumps(message_data) + "\n").encode("utf-8"))

        except Exception as e:
            print(f"❌ Error enviando mensaje: {e}")

    def start_chat(self):
        """Inicia el loop principal del chat"""
        if not self.connected:
            print("❌ No conectado al servidor")
            return

        print("\n💬 Chat iniciado. Escribe 'quit' para salir\n")

        try:
            while True:
                message = input()
                if message.lower() == "quit":
                    break
                elif message.strip():
                    self.send_message(message)

        except KeyboardInterrupt:
            print("\n👋 Cerrando chat...")
        finally:
            self.disconnect()

    def disconnect(self):
        """Desconecta del servidor"""
        self.connected = False
        if self.socket:
            self.socket.close()
        print("🔌 Desconectado del servidor")


if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("🔒 Chat Cifrado con Diffie-Hellman + AES-256")
    print("=" * 60)
    print()

    # Aceptar argumentos de línea de comandos o usar input()
    if len(sys.argv) == 4:
        # Modo automático: python3 client.py <username> <host> <port>
        username = sys.argv[1]
        host = sys.argv[2]
        port = int(sys.argv[3])
    else:
        # Modo interactivo
        username = input("👤 Ingresa tu nombre de usuario: ").strip()
        if not username:
            print("❌ Nombre de usuario requerido")
            exit(1)

        host = input("🌐 IP del servidor (Enter para localhost): ").strip()
        if not host:
            host = "localhost"

        port_input = input("🔌 Puerto (Enter para 8888): ").strip()
        port = int(port_input) if port_input else 8888

    client = SecureChatClient(username)
    client.connect(host=host, port=port)

    if client.connected:
        client.start_chat()
