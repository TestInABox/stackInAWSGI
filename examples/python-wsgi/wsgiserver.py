from __future__ import absolute_import

from wsgiref.simple_server import make_server

import app


httpd = make_server('localhost', 8081, app.app)
httpd.serve_forever()
