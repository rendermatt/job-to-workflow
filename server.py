from http.server import HTTPServer, BaseHTTPRequestHandler
from main import calculate_and_process

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        digits = [int(c) for c in self.path if c.isdigit()]
        result = calculate_and_process(*digits)
        body = str(result).encode()
        self.send_response(200)
        self.end_headers()
        self.wfile.write(body)

if __name__ == "__main__":
    HTTPServer(("", 8080), Handler).serve_forever()
