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

import logging
import os
import urlparse

from tornado.options import options
from tornado.template import Loader
from tornado.web import Application

from ming.datastore import DataStore

from apollo.server.protocol.transport import Transport
from apollo.server.web import FrontendHandler, SessionHandler, ActionHandler, EventsHandler, DylibHandler
from apollo.server.cron import CronScheduler
from apollo.server.dylib.meta import DylibDispatcher
from apollo.server.messaging.bus import Bus

from apollo.server.models.meta import bind_session

class Core(Application):
    def __init__(self):
        logging.getLogger().setLevel(options.logging_level)

        # apollo distribution root
        dist_root = os.path.join(os.path.dirname(__file__), "..", "..")

        Application.__init__(
            self,
            [
                (r"/",                  FrontendHandler),
                (r"/session",           SessionHandler),
                (r"/action",            ActionHandler),
                (r"/events",            EventsHandler),
                (r"/dylib/(.*)\.js",    DylibHandler)
            ],
            dist_root   =   dist_root,
            static_path =   os.path.join(dist_root, "static")
        )

        self.loader = Loader(os.path.join(dist_root, "template"))

        self.setupSession()

        self.dylib_dispatcher = DylibDispatcher(self)

        self.connections = {}

        self.setupCron()

        self.bus = Bus(self)

    # setup
    def setupSession(self):
        # netloc for mongodb
        mongodb_netloc = options.mongodb_host
        if options.mongodb_port:
            mongodb_netloc += ":%d" % options.mongodb_port
        if options.mongodb_username:
            mongodb_auth = options.mongodb_username
            if options.mongodb_password:
                mongodb_auth += ":%s" % options.mongodb_password
            mongodb_netloc = mongodb_auth + "@" + mongodb_netloc

        bind_session(DataStore(urlparse.urlunsplit((
            "mongodb",
            mongodb_netloc,
            "",
            "",
            ""
        )), database=options.mongodb_database))

    def setupCron(self):
        self.cron = CronScheduler(self)
        self.cron.go()

    # transport related stuff
    def createTransport(self):
        transport = Transport(self)
        self.connections[transport.token] = transport
        return transport

    def getTransport(self, token):
        return self.connections[token]

    def loseTransport(self, token):
        transport = self.connections[token]
        del self.connections[token]

        logging.info("Lost transport: %s" % token)