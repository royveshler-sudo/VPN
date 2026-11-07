import socket
import ssl

ADDR = ('0.0.0.0', 8080)

s_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s_sock.bind(ADDR)
s_sock.listen(2)

print(f"[Target Server] Listening on {ADDR}...")

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

context.set_ciphers('DEFAULT:@SECLEVEL=0')

context.load_cert_chain(certfile='keycert.pem')

sock = context.wrap_socket(s_sock, server_side=True)

clientsock, addr = sock.accept()
print(f"[Target Server] Connected from {addr}")

while True:
    data = clientsock.recv(65535)
    if not data:
        break
    print(f"[Target Server] Received data: {data}")
    clientsock.sendall(b"HTTP/1.1 200 OK\r\n\r\nHello Back")

clientsock.close()
sock.close()