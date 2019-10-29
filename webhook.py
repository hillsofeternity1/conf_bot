#!/usr/bin/env python
# -*- coding: utf-8 -*-

from http.server import HTTPServer, SimpleHTTPRequestHandler, CGIHTTPRequestHandler
from socketserver import BaseServer
import ssl
import json
import settings

# fuckin dirty hack. idk the best way to inherit return func into
# RequestHandler class


class RequestHandler(SimpleHTTPRequestHandler):
    def __init__(self,
                 request,
                 client_address,
                 server):
        self.worker = settings.worker
        super(RequestHandler, self).__init__(
            request=request,
            client_address=client_address,
            server=server)

    def do_POST(self):
        """Serve a POST request."""
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()

        length = self.headers.get('content-length')
        post_body = self.rfile.read(int(length))
        msg = json.loads(post_body.decode("utf-8"))
        self.worker.handleUpdate(msg)

    def do_GET(self):
        pass


class WebHook:
    def __init__(self,
                 certfile,
                 keyfile,
                 address=settings.parser.get('bot', 'bind_address'),
                 port=8443,
                 RequestHandler=RequestHandler):

        self.httpd = HTTPServer((address, port), RequestHandler)
        self.httpd.socket = ssl.wrap_socket(self.httpd.socket,
                                            certfile=certfile,
                                            keyfile=keyfile,
                                            server_side=True)

    def serve(self):
        try:
            self.httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print("ERROR: %s" % e)
        finally:
            # Clean-up server (close socket, etc.)
            self.httpd.server_close()
