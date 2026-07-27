import socket

conn = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)


conn.bind(("127.0.0.1", 8000))
conn.listen(1)

while True:
    incoming_connection, client_address = conn.accept()
    bytes_recv = incoming_connection.recv(256)

    def parse_request(bytes_recv):
        decoded = bytes_recv.decode()
        head, _, body = decoded.partition("\r\n\r\n")
        lines = head.split("\r\n")

        request_line = lines[0]
        method, path, version = request_line.split(" ")

        headers = {}
        for line in lines[1:]:
            k, v = line.split(": ", 1)
            headers[k] = v

        return{
            "method": method,
            "path": path,
            "version": version,
            "headers": headers,
            "body": body
        }
    
    parsed = parse_request(bytes_recv)
    print(parsed)

    
    body = "hello\n"
    content_length = len(body)
    
    response = f'HTTP/1.1 200 OK\r\nContent-Length: {content_length-1}\r\n\r\n{body}'
    encoded_resp = response.encode()


    print(repr(encoded_resp))
    incoming_connection.send(encoded_resp)

    print(bytes_recv)
    
    incoming_connection.close()


