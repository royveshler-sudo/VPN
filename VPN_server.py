import socket
from AESCryptoHandler import AESCryptoHandler


def initialize_server_socket(server_ip: str, server_port: int) -> socket.socket:
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind((server_ip, server_port))
    server_sock.listen(1)
    return server_sock


def accept_client_connection(server_sock: socket.socket):
    conn, client_addr = server_sock.accept()
    return conn, client_addr


def receive_packet_from_client(conn: socket.bytes) -> bytes:
    raw_length = conn.recv(4)
    if not raw_length:
        return b""
    msg_length = int.from_bytes(raw_length, 'big')

    encrypted_data = b""
    while len(encrypted_data) < msg_length:
        chunk = conn.recv(msg_length - len(encrypted_data))
        if not chunk:
            break
        encrypted_data += chunk
    return encrypted_data


SERVER_IP = "0.0.0.0"
SERVER_PORT = 5000
SHARED_KEY = b'YOUR_SHARED_SECRET_KEY_HERE_32_BYTES=='


def server_main():
    crypto = AESCryptoHandler(SHARED_KEY)
    server_sock = initialize_server_socket(SERVER_IP, SERVER_PORT)
    print(f"Server listening on {SERVER_IP}:{SERVER_PORT} ")

    conn, client_addr = accept_client_connection(server_sock)
    print(f"Client connected from {client_addr}")

    try:
        while True:
            encrypted_data = receive_packet_from_client(conn)
            if not encrypted_data:
                break

            # שימוש במחלקה לפענוח
            decrypted_data = crypto.decrypt(encrypted_data)
            print(f"Received and decrypted {len(decrypted_data)} bytes from tunnel.")

    except Exception as e:
        print(f"Server Error: {e}")
    finally:
        conn.close()
        server_sock.close()


if __name__ == "__main__":
    server_main()