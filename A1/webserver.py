"""
NAME: JOENG, SEUNG WON
"""
import sys
# To use arguments
import socket
import os.path

def receive(client_connection):
    request_data = b''
    while True:
      new_data = client_connection.recv(4098)
      if (len(new_data) == 0):
        # client disconnected
        return None, None
      request_data += new_data
      if b'\r\n\r\n' in request_data:
        break

    parts = request_data.split(b'\r\n\r\n', 1)
    header = parts[0]
    body = parts[1]

    if b'Content-Length' in header:
      headers = header.split(b'\r\n')
      for h in headers:
        if h.startswith(b'Content-Length'):
          blen = int(h.split(b' ')[1]);
          break
    else:
        blen = 0

    while len(body) < blen:
      body += client_connection.recv(4098)
      
    header = header.decode('UTF-8')
    body = body.decode('UTF-8')
    
    print(header, flush=True)
    print('')
    print(body, flush=True)

    return header, body


HOST,PORT,ROOT = sys.argv[1], sys.argv[2], sys.argv[3] # arguments

listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listen_socket.bind((HOST, int(PORT)))
listen_socket.listen(1)
print(f'Serving HTTP on port {PORT} ...')

notFound = """\
HTTP/1.1 200 OK
Content-Type: text/html; charset=UTF-8

"""

notFound = notFound.replace('\n', '\r\n')
notFound += """
<html>
<body>
404 File not found
</body>
</html>

"""

notFound = notFound.encode(encoding='UTF-8')

while True:
    client_connection, client_address = listen_socket.accept()
    header, body = receive(client_connection)
    if header is None or body is None:
        client_connection.close()
        continue
    header = header.split('\r\n')
    request_data = header[0].split(' ')
    request_data = request_data[1]
    browser = header[2].split(' ')[-1]

    if 'Firefox' in browser:
        http_response = """\
HTTP/1.1 200 OK
Content-Type: text/html; charset=UTF-8
Connection: close

"""
        http_response = http_response.replace('\n','\r\n')
        http_response += """
<html>
<body>
Please Switch a browser
</body>
</html>

"""
        http_response = http_response.encode(encoding='UTF-8')
    else:
        new_root  = ROOT + request_data
        print(new_root)
        if 'jpg' in request_data:
            if os.path.exists(new_root):
                http_response = """\
HTTP/1.1 200 OK
Content-Type: image/jpeg

"""
                http_response = http_response.replace('\n','\r\n')
                http_response = http_response.encode(encoding='UTF-8')
                with open(new_root, 'rb') as fh:
                    http_response += fh.read()
            else:
                http_response = notFound

        elif 'png' in request_data:
            if os.path.exists(new_root):
                http_response = """\
HTTP/1.1 200 OK
Content-Type: image/png

"""
                http_response = http_response.replace('\n','\r\n')
                http_response = http_response.encode(encoding='UTF-8')
                with open(new_root, 'rb') as fh:
                    http_response += fh.read()
            else:
                http_response = notFound
                
        elif 'html' in request_data:
            if os.path.exists(new_root):
                http_response = """\
HTTP/1.1 200 OK
Content-Type: text/html; charset=UTF-8

"""
                http_response = http_response.replace('\n','\r\n')
                http_response = http_response.encode(encoding='UTF-8')
                with open(new_root, 'rb') as fh:
                    http_response += fh.read()
            else:
                http_response = notFound
    
        else:
            http_response = """\
HTTP/1.1 200 OK
Content-Type: text/html; charset=UTF-8

"""
            http_response = http_response.replace('\n','\r\n')
            http_response += """
<html>
<body>
Not supporting format
</body>
</html>

"""
            http_response = http_response.replace('\n','\r\n')
            http_response = http_response.encode(encoding='UTF-8')

    client_connection.sendall(http_response)
    client_connection.close()
