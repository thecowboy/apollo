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
Apollo server core package.
"""

import urlparse
import logging

from ming.datastore import DataStore

from apollo.server.models.meta import bindSession

from tornado.options import define, options

def setupOptions():
    """
    Initialize options for use with Tornado.
    """
    define("address", default="127.0.0.1", help="bind to the given address", metavar="ADDRESS")
    define("port", default=8081, help="run on the given port", type=int, metavar="PORT")

    define("render_process_num", default=4, help="number of renderer processes to run", type=int, metavar="NUM")

    define("cron_interval", default=3600, help="run cron every specified seconds", type=int, metavar="INTERVAL")

    define("session_expiry", default=3600, help="expire inactive sessions after specified seconds", type=int, metavar="EXPIRY")

    define("mongodb_host", default="localhost", help="mongodb server host", metavar="HOST")
    define("mongodb_port", default=27017, help="mongodb server port", type=int, metavar="PORT")
    define("mongodb_username", default="", help="mongodb server username", metavar="USERNAME")
    define("mongodb_password", default="", help="mongodb server password (put in apollod.conf)", metavar="PASSWORD")
    define("mongodb_database", default="apollo", help="mongodb database name", metavar="DATABASE")

    define("zmq_transport", default="inproc", help="zmq transport", metavar="TYPE")
    define("zmq_host", default="apollo", help="zmq host", metavar="HOST")

    define("logging_level", default=logging.WARN, help="logging level", type=int, metavar="LEVEL")

def setupDBSession():
    """
    Set up the session for Ming (MongoDB).
    """
    # netloc for mongodb
    mongodb_netloc = options.mongodb_host
    if options.mongodb_port:
        mongodb_netloc += ":%d" % options.mongodb_port
    if options.mongodb_username:
        mongodb_auth = options.mongodb_username
        if options.mongodb_password:
            mongodb_auth += ":%s" % options.mongodb_password
        mongodb_netloc = mongodb_auth + "@" + mongodb_netloc

    bindSession(DataStore(urlparse.urlunsplit((
        "mongodb",
        mongodb_netloc,
        "",
        "",
        ""
    )), database=options.mongodb_database))
