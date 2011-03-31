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

"""
The heart of the Apollo server.
"""

import logging
import os

from tornado.options import options
from tornado.template import Loader
from tornado.web import Application

from apollo.server import setupDBSession

from apollo.server.render.supervisor import RendererSupervisor
from apollo.server.web import FrontendHandler, SessionHandler, ActionHandler, EventsHandler, DylibHandler
from apollo.server.cron import CronScheduler
from apollo.server.dylib.meta import DylibDispatcher
from apollo.server.messaging.bus import Bus

class Core(Application):
    """
    The very core of Apollo. Everything depends on this.
    """
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

        setupDBSession()

        self.dylib_dispatcher = DylibDispatcher(self)

        self.connections = {}

        self.bus = Bus(self)

    def go(self):
        """
        Start the server proper.
        """
        self.cron = CronScheduler(self)
        self.cron.go()

        #self.rendervisor = RendererSupervisor()
        #self.rendervisor.go()
