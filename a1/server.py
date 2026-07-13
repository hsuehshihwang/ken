#!/usr/bin/env python3
"""
Simple HTTP server for serving the A1 English content.
Run this to serve files locally so the HTML players work correctly.
"""

import http.server
import socketserver
import sys
import os

PORT = 8000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    
    with socketserver.TCPServer(("", port), Handler) as httpd:
        print(f"\n{'='*50}")
        print(f"A1 English Server")
        print(f"{'='*50}")
        print(f"\nServing at: http://localhost:{port}")
        print(f"\nPages:")
        print(f"  - Main:        http://localhost:{port}/index.html")
        print(f"  - Stories:     http://localhost:{port}/topic/story/index.html")
        print(f"  - 3 Little Pigs: http://localhost:{port}/topic/story/three-little-pigs/index.html")
        print(f"\nPress Ctrl+C to stop.")
        print(f"{'='*50}\n")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")

if __name__ == "__main__":
    main()
