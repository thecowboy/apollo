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

from tornado.options import define

def setup_options():
    define("address", default="127.0.0.1", help="bind to the given address", metavar="ADDRESS")
    define("port", default=8081, help="run on the given port", type=int, metavar="PORT")

    define("cron_interval", default=3600, help="run cron every specified seconds", type=int, metavar="INTERVAL")

    define("session_expiry", default=3600, help="expire inactive sessions after specified seconds", type=int, metavar="EXPIRY")

    define("mongodb_host", default="localhost", help="mongodb server host", metavar="HOST")
    define("mongodb_port", default=27017, help="mongodb server port", type=int, metavar="PORT")
    define("mongodb_username", default="", help="mongodb server username", metavar="USERNAME")
    define("mongodb_password", default="", help="mongodb server password (put in apollod.conf)", metavar="PASSWORD")
    define("mongodb_database", default="apollo", help="mongodb database name", metavar="DATABASE")

    define("logging_level", default=logging.WARN, help="logging level", type=int, metavar="LEVEL")
