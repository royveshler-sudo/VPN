import socket
import pydivert
from AESCryptoHandler import AESCryptoHandler


def connect_to_vpn_server(server_ip: str, server_port: int) -> socket.socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((server_ip, server_port))
    return sock


def initialize_packet_capture(filter_string="outbound and tcp.DstPort == 80"):
    w = pydivert.WinDivert(filter_string)
    w.open()
    return w


def send_encrypted_packet_to_server(sock: socket.socket, encrypted_data: bytes):
    data_length = len(encrypted_data).to_bytes(4, 'big')
    sock.sendall(data_length + encrypted_data)


def receive_encrypted_response(sock: socket.socket) -> bytes:
    raw_length = sock.recv(4)
    if not raw_length:
        return b""
    msg_length = int.from_bytes(raw_length, 'big')

    encrypted_data = b""
    while len(encrypted_data) < msg_length:
        chunk = sock.recv(msg_length - len(encrypted_data))
        if not chunk:
            break
        encrypted_data += chunk
    return encrypted_data


def decrypt_response(crypto: AESCryptoHandler, encrypted_data: bytes) -> bytes:
    return crypto.decrypt(encrypted_data)


def inject_packet_to_os(w_handle, decrypted_data: bytes):
    try:
        packet = pydivert.Packet(decrypted_data)
        w_handle.send(packet)
    except Exception as e:
        print(f"[Client] Injection error: {e}")


SERVER_IP = "127.0.0.1"
SERVER_PORT = 5000
SHARED_KEY = b'kpOl0dJoPHXokGKiL-T21ZJzE06cVBhcJF441Hg22aU='


def client_main():
    crypto = AESCryptoHandler(SHARED_KEY)
    sock = connect_to_vpn_server(SERVER_IP, SERVER_PORT)
    print("Client connected to VPN server.")

    w = initialize_packet_capture("outbound and tcp.DstPort == 80")
    with w:
        print("Packet capture started (Outbound TCP port 80).")
        for packet in w:
            try:
                encrypted_data = crypto.encrypt(packet.raw)
                send_encrypted_packet_to_server(sock, encrypted_data)

                encrypted_response = receive_encrypted_response(sock)
                if not encrypted_response:
                    print("Client Server closed connection.")
                    break

                decrypted_data = decrypt_response(crypto, encrypted_response)

                if decrypted_data:
                    inject_packet_to_os(w, decrypted_data)
                    print(f"Client Received, decrypted, and injected {len(decrypted_data)} bytes back to OS.")

            except Exception as e:
                print(f"Error: {e}")


if __name__ == "__main__":
    client_main()