"""
🌐 Standalone Web Server for the Command Center
Runs a high-performance local server and opens the dashboard directly in your browser.
"""

import os
import sys
import webbrowser
from http.server import SimpleHTTPRequestHandler, HTTPServer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def find_available_port(start_port=8080, max_attempts=10):
    import socket
    for p in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    return start_port


def run_server():
    os.chdir(BASE_DIR)
    
    # Always ensure freshest dashboard HTML and all screen pages are written
    from generate_separate_pages import build_all_pages
    build_all_pages()

    port = find_available_port(8080)
    server_address = ("", port)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    
    url = f"http://localhost:{port}/index.html"
    print("=" * 65)
    print("  🛰️ AURA-FIRE: AI INDUSTRIAL FIRE COMMAND CENTER")
    print("=" * 65)
    print(f"👉 Link to open in browser: {url}")
    print("=" * 65)
    
    try:
        webbrowser.open(url)
    except Exception:
        pass

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer terminated cleanly.")
        sys.exit(0)


if __name__ == "__main__":
    run_server()
