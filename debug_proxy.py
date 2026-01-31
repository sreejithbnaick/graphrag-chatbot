import http.server
import ssl
import urllib.request
import urllib.error
import os

# Generate a self-signed cert if it doesn't exist
os.system("openssl req -new -newkey rsa:2048 -days 365 -nodes -x509 -keyout key.pem -out cert.pem -subj '/CN=localhost'")

class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args): pass

    def handle_request(self, method):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else None
        
        print(f"\n--- [HTTPS {method}] Request ---")
        print(f"Path: {self.path}")
        
        lm_url = f"http://localhost:1234{self.path}"
        req = urllib.request.Request(lm_url, data=body, method=method)
        
        for k, v in self.headers.items():
            if k.lower() != 'host':
                req.add_header(k, v)
        
        try:
            # We don't care about SSL for the internal forward to LM Studio
            with urllib.request.urlopen(req) as response:
                resp_body = response.read()
                print(f"--- LM Studio Response ({response.status}) ---")
                self.send_response(response.status)
                for k, v in response.getheaders():
                    if k.lower() not in ['content-encoding', 'transfer-encoding', 'content-length']:
                        self.send_header(k, v)
                self.send_header('Content-Length', str(len(resp_body)))
                self.end_headers()
                self.wfile.write(resp_body)
        except Exception as e:
            print(f"Error forwarding: {e}")
            self.send_error(500, str(e))

    def do_POST(self): self.handle_request('POST')
    def do_GET(self): self.handle_request('GET')

def run(port=1235):
    server_address = ('', port)
    httpd = http.server.HTTPServer(server_address, ProxyHandler)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('cert.pem', 'key.pem')
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
    print(f"HTTPS Proxy running on port {port}...")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
