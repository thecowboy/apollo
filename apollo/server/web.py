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

from tornado.options import options
from tornado.web import RequestHandler, asynchronous

from apollo.server.models import meta
from apollo.server.models.session import Session

class FrontendHandler(RequestHandler):
    def get(self):
        self.set_header("Content-Type", "text/html; charset=utf8")
        self.write(self.application.loader.load("frontend.html").generate())

class SessionHandler(RequestHandler):
    SUPPORTED_METHODS = ("GET",)

    def get(self, *args, **kwargs):
        self.set_header("Content-Type", "application/json")
        session = Session()
        meta.session.flush_all()
        self.write(str(session._id))

class ActionHandler(RequestHandler):
    SUPPORTED_METHODS = ("POST",)

    def post(self, *args, **kwargs):
        self.finish()

class EventsHandler(RequestHandler):
    SUPPORTED_METHODS = ("GET",)

    @asynchronous
    def get(self, *args, **kwargs):
        session_id = self.get_argument("s")
        self.set_header("Content-Type", "application/json")

class DylibHandler(RequestHandler):
    SUPPORTED_METHODS = ("GET",)

    def get(self, pathspec, *args, **kwargs):
        self.set_header("Content-Type", "text/javascript")
        self.write(self.application.dylib_dispatcher.dispatch(pathspec))
