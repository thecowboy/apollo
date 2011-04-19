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
import urllib
import logging

from sqlalchemy.engine import create_engine

from apollo.server.models.meta import bindSession

from tornado.options import define, options, parse_config_file, parse_command_line
from tornado.options import Error as OptionsError

def skeletonSetup():
    try:
        setupOptions()
    except OptionsError:
        # if we're using multiprocessing, stuff might happen that causes weird
        # double definitions
        #
        # TODO: i don't know the exact cause of this yet. investigate
        pass
    parse_config_file("apollod.conf")
    parse_command_line()
    setupDBSession()

def setupOptions():
    """
    Initialize options for use with Tornado.
    """
    define("debug", default=False, help="run in debug mode", type=bool, metavar="DEBUG")

    define("address", default="127.0.0.1", help="bind to the given address", metavar="ADDRESS")
    define("port", default=8081, help="run on the given port", type=int, metavar="PORT")

    define("plugins", default=[], help="plugins to load", type=list, metavar="PLUGINS")

    define("render_process_num", default=4, help="number of renderer processes to run", type=int, metavar="NUM")

    define("cron_interval", default=360, help="run cron every specified seconds", type=int, metavar="INTERVAL")

    define("session_expiry", default=3600, help="expire inactive sessions after specified seconds", type=int, metavar="EXPIRY")

    define("sql_store", default="postgresql", help="sql server store", metavar="HOST")
    define("sql_host", default="localhost", help="sql server host", metavar="HOST")
    define("sql_port", default=5432, help="sql server port", type=int, metavar="PORT")
    define("sql_username", default="apollo", help="sql server username", metavar="USERNAME")
    define("sql_password", default="apollo", help="sql server password (put in apollod.conf)", metavar="PASSWORD")
    define("sql_database", default="apollo", help="sql database name", metavar="DATABASE")

    define("amqp_host", default="localhost", help="amqp server host", metavar="HOST")
    define("amqp_port", default=5672, help="amqp server port", type=int, metavar="PORT")
    define("amqp_username", default="guest", help="amqp server username", metavar="USERNAME")
    define("amqp_password", default="guest", help="amqp server password (put in apollod.conf)", metavar="PASSWORD")
    define("amqp_vhost", default="/", help="amqp vhost", metavar="VHOST")

    define("logging_level", default=logging.WARN, help="logging level", type=int, metavar="LEVEL")

def setupDBSession():
    """
    Set up the session for SQLAlchemy.
    """
    # netloc
    netloc = options.sql_host
    if options.sql_port:
        netloc += ":%d" % options.sql_port
    if options.sql_username:
        auth = urllib.unquote_plus(options.sql_username)
        if options.sql_password:
            auth += ":%s" % urllib.unquote_plus(options.sql_password)
        netloc = auth + "@" + netloc

    bindSession(create_engine(urlparse.urlunsplit((
        options.sql_store,
        netloc,
        options.sql_database,
        "",
        ""
    ))))
