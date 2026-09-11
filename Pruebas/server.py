from http.server import BaseHTTPRequestHandler, HTTPServer
import socket

class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        hostname = socket.gethostname()

        response = f"""
        <html>
        <head>
            <title>Kubernetes Demo</title>
        </head>
        <body>
            <h1>Hola desde Kubernetes!</h1>
            <p><strong>Pod:</strong> {hostname}</p>
        </body>
        </html>
        """

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(response.encode())

server = HTTPServer(("0.0.0.0", 8080), Handler)

print("Server running on port 8080")

server.serve_forever()
