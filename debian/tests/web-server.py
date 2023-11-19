#!/usr/bin/python3

# Taken from Flatpak

# Copyright 2017-2019 Red Hat, Inc.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#
# On Debian systems, the full text of the GNU Lesser General Public License
# version 2.1 can be found in the file '/usr/share/common-licenses/LGPL-2.1'.

from wsgiref.handlers import format_date_time
from email.utils import parsedate
from calendar import timegm
import gzip
import sys
import time
import zlib
import os
from http import HTTPStatus
from urllib.parse import parse_qs
import http.server as http_server
from io import BytesIO
import sys

class RequestHandler(http_server.SimpleHTTPRequestHandler):
    def handle_tokens(self):
        need_token_path = self.translate_path(self.path) + ".need_token"
        if os.path.isfile(need_token_path):
            with open(need_token_path, 'r') as content_file:
                token_content = content_file.read()
            token = None
            auth = self.headers.get("Authorization")
            if auth and auth.startswith("Bearer "):
                token = auth[7:]
            if token == None:
                self.send_response(HTTPStatus.UNAUTHORIZED, "No token")
                self.end_headers()
                return True
            if token != token_content:
                self.send_response(HTTPStatus.UNAUTHORIZED, "Wrong token")
                self.end_headers()
                return True
        return False

    def do_GET(self):
        if self.handle_tokens():
            return None
        return super().do_GET()

def run(dir):
    RequestHandler.protocol_version = "HTTP/1.0"
    httpd = http_server.HTTPServer( ("127.0.0.1", 0), RequestHandler)
    host, port = httpd.socket.getsockname()[:2]
    with open("httpd-port", 'w') as file:
        file.write("%d" % port)
    with open("httpd-pid", 'w') as file:
        file.write("%d" % os.getpid())
    try:
        os.write(3, bytes("Started\n", 'utf-8'));
    except:
        pass
    print("Serving HTTP on port %d" % port);
    if dir:
        os.chdir(dir)
    httpd.serve_forever()

if __name__ == '__main__':
    dir = None
    if len(sys.argv) >= 2 and len(sys.argv[1]) > 0:
        dir = sys.argv[1]

    run(dir)
