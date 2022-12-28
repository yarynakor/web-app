import datetime
import json
import mimetypes
import pathlib
import socket
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import concurrent.futures

new_dict = {}


class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('index.html')
        elif pr_url.path == '/message':
            self.send_html_file('message.html')
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file('error.html', 404)

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())

    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()


def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('', 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


if __name__ == '__main__':
    run()


UDP_IP = '127.0.0.1'
UDP_PORT = 5000


def run_server(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = ip, port
    sock.bind(server)
    try:
        while True:
            data, address = sock.recvfrom(1024)
            print(f'Received data: {data.decode()} from: {address}')
            data_parse = urllib.parse.unquote_plus(data.decode())
            data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
            print(data_dict)
            new_dict[str(datetime.now())] = data_dict
            with open('web app/storage/data.json', 'w') as file:
                json.dump(new_dict, file, indent=4, separators=(',', ': '))
                sock.sendto(data, address)
                print(f'Server: send data {data.decode()} to: {address}')

    except KeyboardInterrupt:
        print(f'Destroy server')
    finally:
        sock.close()


if __name__ == '__main__':
    with concurrent.futures.ProcessPoolExecutor(4) as executor:
        run_server(UDP_IP, UDP_PORT)


UDP_IP = '127.0.0.1'
UDP_PORT = 5000


def run_client(ip: str, port: int, data=None):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        server = ip, port
        client.sendto(data, server)
        print(f'Send data:{data.decode()} to server: {server}')
        response, address = client.recvfrom(1024)
        print(f'Response data: {response.decode()} from address: {address}')


if __name__ == '__main__':
    with concurrent.futures.ProcessPoolExecutor(4) as executor:
        run_server(UDP_IP, UDP_PORT)

