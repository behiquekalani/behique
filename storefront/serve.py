#!/usr/bin/env python3
"""
Behike Storefront Server
Serves the static storefront on port 8080.
Run: python3 serve.py
"""

import http.server
import socketserver
import os
import sys

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))


class CORSHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler with CORS headers for local development."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        sys.stdout.write("[%s] %s\n" % (self.log_date_time_string(), format % args))
        sys.stdout.flush()


def main():
    with socketserver.TCPServer(("0.0.0.0", PORT), CORSHandler) as httpd:
        print(f"Behike Storefront")
        print(f"Serving on http://0.0.0.0:{PORT}")
        print(f"Directory: {DIRECTORY}")
        print(f"Press Ctrl+C to stop.\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down.")
            httpd.shutdown()


if __name__ == "__main__":
    main()
