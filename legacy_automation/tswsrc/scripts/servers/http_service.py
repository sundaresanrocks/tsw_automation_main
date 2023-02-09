__author__ = 'manoj'
import logging

from http.server import HTTPServer, BaseHTTPRequestHandler, SimpleHTTPRequestHandler
import sys
import os
import base64
import ssl
import cgi
HTTP_LOG_FILE = '/tmp/http_service.log'
KEY = ''

class ServerHandler(SimpleHTTPRequestHandler):

    def do_GET(self):
        logging.debug("======= GET STARTED =======")
        logging.debug(self.headers)
        with open(HTTP_LOG_FILE, 'a') as fpw:
            fpw.write(str(self.headers))
        SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        logging.debug("======= POST STARTED =======")
        logging.debug(self.headers)
        with open(HTTP_LOG_FILE, 'a') as fpw:
            fpw.write(self.headers)
            fpw.write('\n')
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST',
                     'CONTENT_TYPE': self.headers['Content-Type'],
                     })
        logging.debug("======= POST VALUES =======")
        for item in form.list:
            logging.warning(item)
            with open(HTTP_LOG_FILE, 'w+') as fpw:
                fpw.write(str(item))
                fpw.write('\n')
        logging.debug("\n")
        SimpleHTTPRequestHandler.do_GET(self)


def https_server():

    httpd = HTTPServer(('localhost', 4443), ServerHandler)
    httpd.socket = ssl.wrap_socket(httpd.socket, certfile='path/to/localhost.pem', server_side=True)
    httpd.serve_forever()



class AuthHandler(SimpleHTTPRequestHandler):
    """Main class to present for authentication."""
    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_AUTHHEAD(self):
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm=\"Test\"')
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        """Present frontpage with user authentication. """
        global KEY
        with open(HTTP_LOG_FILE, 'a') as fpw:
            fpw.write(str(self.headers))
        logging.warning(self.headers['Authorization'])
        if self.headers['Authorization'] is None:
            self.do_AUTHHEAD()
            self.wfile.write(b'no auth header received')
            pass
        elif bytes(self.headers['Authorization'], encoding='UTF-8') == b'Basic '+KEY:
            SimpleHTTPRequestHandler.do_GET(self)
            pass
        else:
            self.do_AUTHHEAD()
            self.wfile.write(bytes(self.headers['Authorization'], encoding='UTF-8'))
            self.wfile.write(b'not authenticated')
            pass

def http_server(port, path):

    handler = AuthHandler
    # handler = ServerHandler
    # handler = SimpleHTTPRequestHandler
    os.chdir(path)
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, handler)
    httpd.serve_forever()


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("usage http_service.py port [username:password] [path]")
        sys.exit()
    KEY = base64.b64encode(bytes(sys.argv[2], encoding='UTF-8'))
    _port = int(sys.argv[1])
    _path = sys.argv[3]
    # KEY = base64.b64encode(b'[user:pass]')
    http_server(_port, _path)
