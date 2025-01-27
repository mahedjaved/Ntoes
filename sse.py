import http.server
from http.server import BaseHTTPRequestHandler


class SSEServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Testing SSE...\n")

    def do_WSGet(self, path):
        self.send_response(101)
        self.end_headers()
        ws_message = b"ws-event\n"
        ws_message += b"MESSAGE"
        self.wfile.write(ws_message)


if __name__ == "__main__":
    host = "localhost"
    port = 8080
    server = http.server.HTTPServer((host, port), SSEServer)
    print(f"Serving SSE on {host}:{port}")
    server.serve_forever()
