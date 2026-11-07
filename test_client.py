import socket
import ssl

ADDR = ('192.168.7.18', 8080)

context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

tcpCliSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock = context.wrap_socket(tcpCliSocket)

print("[Test Client] Connecting to target server")
sock.connect(ADDR)

message = b"Hello World"
sock.sendall(message)
print(f"[Test Client] Sent: {message}")

response = sock.recv(65535)
print(f"[Test Client] Received response: {response}")

sock.close()