import os
from http.server import HTTPServer as BaseHTTPServer, SimpleHTTPRequestHandler

class FileHTTPRequestHandler(SimpleHTTPRequestHandler):
    files = {}

    def do_GET(self):
        filename = self.path.lstrip('/')
        if filename in self.files:
            file_path = self.files[filename]
            if os.path.exists(file_path):
                self.send_response(200)
                self.send_header('Content-Type', 'application/octet-stream')
                self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
                self.end_headers()
                with open(file_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, 'File not found')
        else:
            self.send_error(404, 'File not registered')

class HTTPServer:
    def __init__(self, host='localhost', port=4000):
        self.host = host
        self.port = port
    def log(self,*x):
        pass
    def add_file(self, filename, file_path):
        FileHTTPRequestHandler.files[filename] = file_path

    def start(self):
        server_address = (self.host, self.port)
        self.httpd = BaseHTTPServer(server_address, FileHTTPRequestHandler)
        self.log(f'Starting HTTP server on {self.host}:{self.port}')
        self.httpd.serve_forever()

    def stop(self):
        self.httpd.shutdown()