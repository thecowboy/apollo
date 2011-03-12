#
# Copyright (C) 2011 by Tony Young
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import os
import urlparse

from tornado.options import define, options
from tornado.template import Loader
from tornado.web import Application

from couchdb.client import Database

from apollo.server.web import FrontendHandler, ActionHandler, EventsHandler, DylibHandler
from apollo.server.dylib.dispatch import DylibDispatcher

def setup_options():
    define("address", default="127.0.0.1", help="bind to the given address")
    define("port", default=8081, help="run on the given port", type=int)

    define("couchdb_host", default="localhost", help="couchdb server host")
    define("couchdb_port", default=5984, help="couchdb server port", type=int)
    define("couchdb_username", default="", help="couchdb server username")
    define("couchdb_password", default="", help="couchdb server password")
    define("couchdb_database", default="apollo", help="couchdb database name")

class Core(Application):
    def __init__(self):
        # apollo distribution root
        dist_root = os.path.join(os.path.dirname(__file__), "..", "..")

        # netloc for couchdb
        couchdb_netloc = options.couchdb_host
        if options.couchdb_port:
            couchdb_netloc += ":%d" % options.couchdb_port
        if options.couchdb_username:
            couchdb_auth = options.couchdb_username
            if options.couchdb_password:
                couchdb_auth += ":%s" % options.couchdb_password
            couchdb_netloc = couchdb_auth + "@" + couchdb_netloc

        Application.__init__(
            self,
            [
                (r"/",                  FrontendHandler),
                (r"/action",            ActionHandler),
                (r"/events",            EventsHandler),
                (r"/dylib/(.*)\.js",    DylibHandler)
            ],
            dist_root   =   dist_root,
            static_path =   os.path.join(dist_root, "static")
        )

        self.loader = Loader(os.path.join(dist_root, "template"))
        self.couchdb = Database(urlparse.urlunsplit((
            "http",
            couchdb_netloc,
            options.couchdb_database,
            "",
            ""
        )))
        self.dylib_dispatcher = DylibDispatcher(self)
