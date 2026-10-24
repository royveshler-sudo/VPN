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

def inject_packet_to_os(w_handle, packet):
    w_handle.send(packet)

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5000
SHARED_KEY = b'YOUR_SHARED_SECRET_KEY_HERE_32_BYTES=='

def client_main():
    crypto = AESCryptoHandler(SHARED_KEY)
    sock = connect_to_vpn_server(SERVER_IP, SERVER_PORT)
    print("Client connected to VPN server via TCP.")

    w = initialize_packet_capture("outbound and tcp.DstPort == 80")
    with w:
        for packet in w:
            try:
                # שימוש במחלקה להצפנה
                encrypted_data = crypto.encrypt(packet.raw)
                # שימוש בפונקציית שליחה
                send_encrypted_packet_to_server(sock, encrypted_data)
            except Exception as e:
                print(f"Error: {e}")
                inject_packet_to_os(w, packet)

if __name__ == "__main__":
    client_main()