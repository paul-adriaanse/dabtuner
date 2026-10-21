import http.server
import socketserver
import sys
import urllib.request
import urllib.error

PORT = 8009
WELLE_HOST = "http://127.0.0.1:8008"  # Port where welle-cli web server is running


class ReuseAddrTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


class ProxyDashboardHandler(http.server.SimpleHTTPRequestHandler):

    def do_POST(self):
        # Proxy /channel POST request directly to welle-cli
        if self.path == "/channel":
            content_length = int(self.headers.get("Content-Length", 0))
            payload = self.rfile.read(content_length)

            try:
                req = urllib.request.Request(
                    f"{WELLE_HOST}/channel",
                    data=payload,
                    headers={"Content-Type": "text/plain"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=3) as resp:
                    self.send_response(resp.status)
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(resp.read())
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()

    def do_GET(self):
        # 1. Proxy /mux.json
        if self.path == "/mux.json":
            try:
                req = urllib.request.Request(
                    f"{WELLE_HOST}/mux.json",
                    headers={"User-Agent": "WelleDashboardProxy/1.0"},
                )
                with urllib.request.urlopen(req, timeout=2) as resp:
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.send_header("Cache-Control", "no-cache")
                    self.end_headers()
                    self.wfile.write(resp.read())
            except Exception as e:
                self.send_response(502)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(
                    f'{{"error": "Failed to fetch from welle-cli: {str(e)}"}}'.encode("utf-8")
                )
            return

        # 2. Proxy MOT images, streams, mp3, aac, etc. to welle-cli
        elif (
            self.path.startswith("/mot/")
            or self.path.startswith("/stream/")
            or self.path.startswith("/mp3/")
            or self.path.startswith("/aac/")
        ):
            target_url = f"{WELLE_HOST}{self.path}"
            try:
                req = urllib.request.Request(
                    target_url,
                    headers={"User-Agent": "WelleDashboardProxy/1.0"},
                )
                with urllib.request.urlopen(req, timeout=10) as resp:
                    self.send_response(resp.status)
                    content_type = resp.headers.get("Content-Type", "application/octet-stream")
                    self.send_header("Content-Type", content_type)
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.send_header("Cache-Control", "no-cache")
                    self.end_headers()

                    # Stream data in chunks (handles both binary image responses and continuous audio streams)
                    while True:
                        chunk = resp.read(8192)
                        if not chunk:
                            break
                        self.wfile.write(chunk)
            except urllib.error.HTTPError as e:
                self.send_response(e.code)
                self.end_headers()
            except Exception as e:
                self.send_response(502)
                self.end_headers()
                self.wfile.write(str(e).encode("utf-8"))
            return

        # 3. Default fallback: serve local files (index.html, static assets, etc.)
        return super().do_GET()


if __name__ == "__main__":
    sys.stdout.reconfigure(line_buffering=True)
    print(f"[+] Starting proxy server on port {PORT}...")
    with ReuseAddrTCPServer(("", PORT), ProxyDashboardHandler) as httpd:
        httpd.serve_forever()