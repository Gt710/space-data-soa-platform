import http.server, socketserver, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
print("Frontend running at http://localhost:3000")
socketserver.TCPServer(("", 3000), http.server.SimpleHTTPRequestHandler).serve_forever()
