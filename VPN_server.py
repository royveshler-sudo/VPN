import socket
from AESCryptoHandler import AESCryptoHandler
import pydivert


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

def create_new_packet(decrypted_data: bytes, server_ip: str):
    packet = pydivert.Packet(decrypted_data)
    packet.src_addr = server_ip
    return packet


def send_packet_to_target(target_sock: socket.socket, packet: pydivert.Packet):
    try:
        if packet.payload:
            target_sock.sendall(packet.payload)
    except Exception as e:
        print(f"[Error sending to target]: {e}")

def receive_packet_from_target(target_sock: socket.socket):
    try:
        data = target_sock.recv(65535)
        return data
    except Exception as e:
        print(f"[Error receiving from target]: {e}")
        return b""

def send_packet_to_client(conn: socket.socket, encrypted_data: bytes):
    try:
        data_length = len(encrypted_data).to_bytes(4, 'big')
        conn.sendall(data_length + encrypted_data)

    except Exception as e:
        print(f"[Error sending packet to client]: {e}")


def connect_to_target(packet: pydivert.Packet) -> socket.socket:
    dest_ip = packet.dst_addr
    dest_port = packet.dst_port
    target_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    target_sock.settimeout(5)
    target_sock.connect((dest_ip, dest_port))

    return target_sock


SERVER_IP = "0.0.0.0"
SERVER_PORT = 5000
SHARED_KEY = b'kpOl0dJoPHXokGKiL-T21ZJzE06cVBhcJF441Hg22aU='


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

            decrypted_data = crypto.decrypt(encrypted_data)

            new_packet = create_new_packet(decrypted_data, SERVER_IP)

            if new_packet.tcp and new_packet.payload:
                try:
                    with connect_to_target(new_packet) as target_sock:

                        send_packet_to_target(target_sock, new_packet)

                        response_data = receive_packet_from_target(target_sock)

                        if response_data:
                            encrypted_response = crypto.encrypt(response_data)
                            send_packet_to_client(conn, encrypted_response)
                            print(f"[Server] Sent {len(encrypted_response)} encrypted bytes back to client.")

                except Exception as target_err:
                    print(f"[Server Target Error]: {target_err}")

    except Exception as e:
        print(f"Server Error: {e}")
    finally:
        conn.close()
        server_sock.close()


if __name__ == "__main__":
    server_main()