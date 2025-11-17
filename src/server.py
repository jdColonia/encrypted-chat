import socket
import threading
import json
import time
from crypto_utils import CryptoManager


class SecureChatServer:
    def __init__(self, host="0.0.0.0", port=8888):
        self.host = host
        self.port = port
        self.crypto = CryptoManager()
        self.dh_parameters = None
        self.clients = {}  # {username: socket}
        self.dh_public_keys = {}  # {username: public_key_pem}

    def start(self):
        """Iniciar servidor"""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen(2)

        print("=" * 60)
        print("🔒 Servidor de Chat Seguro con Diffie-Hellman + AES-256")
        print("=" * 60)
        print(f"📡 Escuchando en {self.host}:{self.port}")
        print("💡 El servidor actúa como relay - NO puede descifrar mensajes")

        print("🔐 Generando parámetros Diffie-Hellman...")
        self.crypto.generate_dh_parameters()
        self.dh_parameters = self.crypto.get_dh_parameters_pem()

        print("⏳ Esperando conexiones...\n")

        while True:
            try:
                if len(self.clients) < 2:
                    client_socket, address = server.accept()
                    print(f"🔌 Nueva conexión desde {address}")

                    client_thread = threading.Thread(
                        target=self.handle_client, args=(client_socket, address)
                    )
                    client_thread.start()
                else:
                    time.sleep(0.5)
            except Exception as e:
                print(f"❌ Error fatal en el bucle principal del servidor: {e}")
                break

        print("\n✅ Dos clientes conectados - Chat activo")

    def handle_client(self, client_socket, address):
        """Manejar cliente conectado"""
        try:
            # Recibir información de registro
            data = client_socket.recv(4096).decode("utf-8")
            register_data = json.loads(data)

            # Almacenar cliente
            username = register_data["username"]
            self.clients[username] = client_socket
            print(f"✅ Usuario registrado: {username}")
            
            if username in self.dh_public_keys:
                del self.dh_public_keys[username]

            # Enviar confirmación de registro
            response = {
                "type": "registration_success",
                "message": f"Bienvenido {username}!",
            }
            client_socket.send((json.dumps(response) + "\n").encode("utf-8"))

            # Enviar parámetros DH al cliente
            params_msg = {
                "type": "dh_parameters",
                "parameters": self.dh_parameters.decode("utf-8"),
            }
            client_socket.send((json.dumps(params_msg) + "\n").encode("utf-8"))
            print(f"📤 Parámetros DH enviados a {username}")

            # Escuchar mensajes del cliente
            buffer = ""
            while True:
                # Recibir mensajes del cliente
                data = client_socket.recv(8192).decode("utf-8")
                if not data:
                    break

                buffer += data
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if not line.strip():
                        continue

                    # Cargar mensaje
                    message_data = json.loads(line)
                    msg_type = message_data.get("type")

                    # Manejar mensajes de DH
                    if msg_type == "dh_public_key":
                        # Almacenar llave pública DH
                        self.dh_public_keys[username] = message_data[
                            "public_key"
                        ].encode("utf-8")
                        print(f"📥 Llave pública DH recibida de {username}")

                        # Si ambos usuarios han enviado sus llaves, intercambiarlas
                        if len(self.dh_public_keys) == 2:
                            self.exchange_dh_public_keys()

                    # Manejar mensajes de chat
                    elif msg_type == "chat_message":
                        self.relay_message(username, message_data)

        except Exception as e:
            print(f"❌ Error con cliente {address}: {e}")
        finally:
            # Remover cliente desconectado
            client_socket.close()
            for user, sock in list(self.clients.items()):
                if sock == client_socket:
                    del self.clients[user]
                    if user in self.dh_public_keys:
                        del self.dh_public_keys[user]
                    self.try_reset_key_exchange()
                    print(f"🔌 Cliente {user} desconectado")
                    break

    def exchange_dh_public_keys(self):
        """Intercambiar llaves públicas DH entre los dos usuarios"""
        usernames = list(self.clients.keys())
        user1, user2 = usernames[0], usernames[1]
        print(f"\n🔑 Intercambio de llaves: {user1} ↔ {user2}")

        # Enviar llave pública de user2 a user1
        msg1 = {
            "type": "dh_peer_public_key",
            "from": user2,
            "public_key": self.dh_public_keys[user2].decode("utf-8"),
        }
        self.clients[user1].send((json.dumps(msg1) + "\n").encode("utf-8"))

        # Enviar llave pública de user1 a user2
        msg2 = {
            "type": "dh_peer_public_key",
            "from": user1,
            "public_key": self.dh_public_keys[user1].decode("utf-8"),
        }
        self.clients[user2].send((json.dumps(msg2) + "\n").encode("utf-8"))

        print(f"   ✅ Canal seguro establecido\n")

    def relay_message(self, sender, message_data):
        """Retransmitir mensajes cifrados (el servidor no puede leerlos)"""
        for username, client_socket in self.clients.items():
            if username != sender:
                try:
                    relay_msg = {
                        "type": "encrypted_message",
                        "from": sender,
                        "encrypted_content": message_data["encrypted_content"],
                        "timestamp": time.time(),
                    }
                    client_socket.send((json.dumps(relay_msg) + "\n").encode("utf-8"))
                    print(f"📨 Mensaje cifrado: {sender} -> {username}")
                except Exception as e:
                    print(f"❌ Error enviando mensaje a {username}: {e}")
                    
    def try_reset_key_exchange(self):
        if len(self.dh_public_keys) < 2:
            print("♻ Reiniciando intercambio Diffie-Hellman, falta un cliente")


if __name__ == "__main__":
    # Iniciar servidor
    server = SecureChatServer()
    try:
        server.start()
        # Mantener servidor corriendo
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Cerrando servidor...")
