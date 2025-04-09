import http.server
import socketserver
import threading
import os
import json
from urllib.parse import unquote

# Store the workspace root when initializing the handler factory
WORKSPACE_ROOT = os.getcwd() 

class CarouselPreviewHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Serve files relative to the workspace root
        super().__init__(*args, directory=WORKSPACE_ROOT, **kwargs)

    # Override translate_path to ensure it uses the workspace root correctly
    # This might not be strictly necessary if SimpleHTTPRequestHandler's directory
    # argument works as expected, but it provides clarity.
    def translate_path(self, path):
        path = super().translate_path(path)
        # Ensure the path remains within the workspace root directory for security
        # (although SimpleHTTPRequestHandler should handle this)
        # This prevents accessing files outside the intended directory via '..'
        abs_path = os.path.abspath(path)
        abs_workspace_root = os.path.abspath(WORKSPACE_ROOT)
        if not abs_path.startswith(abs_workspace_root):
            # Return a path that will likely result in a 404 if outside workspace
            return os.path.join(WORKSPACE_ROOT, 'nonexistent') 
        return path

def start_preview_server(port=8000):
    """Start a local HTTP server to preview the carousel"""
    
    # The handler will now serve files from the workspace root
    handler = CarouselPreviewHandler 
    httpd = None

    # Try to bind to the port
    try:
        httpd = socketserver.TCPServer(("", port), handler)
    except OSError as e:
        print(f"Error: Could not bind to port {port}. It might be already in use. {e}")
        return None # Indicate failure

    print(f"Server starting at http://localhost:{port}/")
    print("Serving files from directory:", WORKSPACE_ROOT)
    print("Access the preview at: http://localhost:{port}/preview_html/index.html")
    print("Press Ctrl+C (or Enter in some environments) to stop the server")
    
    server_thread = threading.Thread(target=httpd.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    return httpd # Return the server instance so it can be shut down 