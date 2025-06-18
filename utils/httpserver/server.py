import os
from http.server import HTTPServer as BaseHTTPServer, SimpleHTTPRequestHandler

class FileHTTPRequestHandler(SimpleHTTPRequestHandler):
    files = {}
    def send_head(self):
        filename = self.path.lstrip('/')
        if filename not in self.files:
            self.send_error(404, "File not registered")
            return None

        file_path = self.files[filename]
        if not os.path.isfile(file_path):
            self.send_error(404, "File not found")
            return None

        file_size = os.path.getsize(file_path)
        range_header = self.headers.get('Range')

        if range_header:
            try:
                _, range_spec = range_header.split("=")
                start_str, end_str = range_spec.split("-")
                start = int(start_str) if start_str else 0
                end = int(end_str) if end_str else file_size - 1
                end = min(end, file_size - 1)

                if start > end or start >= file_size:
                    self.send_error(416, "Requested Range Not Satisfiable")
                    return None

                self.send_response(206)
                self.send_header("Content-Type", "application/octet-stream")
                self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
                self.send_header("Content-Length", str(end - start + 1))
                self.send_header("Accept-Ranges", "bytes")
                self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
                self.end_headers()

                return open(file_path, 'rb'), start, end
            except Exception as e:
                self.send_error(400, f"Bad Range Header: {e}")
                return None

        # No range: full content
        self.send_response(200)
        self.send_header("Content-Type", "application/octet-stream")
        self.send_header("Content-Length", str(file_size))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
        self.end_headers()

        return open(file_path, 'rb'), 0, file_size - 1

    def do_GET(self):
        result = self.send_head()
        if result:
            f, start, end = result
            f.seek(start)
            remaining = end - start + 1
            while remaining > 0:
                chunk = f.read(min(64 * 1024, remaining))  # 64KB
                if not chunk:
                    break
                self.wfile.write(chunk)
                remaining -= len(chunk)
            f.close()
        else:
            self.send_error(404, 'File not found')

class HTTPServer:
    def __init__(self, host='0.0.0.0', port=4000):
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