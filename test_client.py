import socket
import ssl

ADDR = ('192.168.7.13', 8080)


tcpCliSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock = ssl.wrap_socket(tcpCliSocket)

print("[Test Client] Connecting to target server...")
sock.connect(ADDR)

message = b"Hello through the VPN tunnel!"
sock.sendall(message)
print(f"[Test Client] Sent: {message}")

response = sock.recv(65535)
print(f"[Test Client] Received response: {response}")

sock.close()