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

from datetime import datetime, timedelta

from tornado.options import options

from zmq.eventloop.ioloop import PeriodicCallback

from ming.orm import Query

from apollo.server.component import Component

from apollo.server.models import meta
from apollo.server.models.session import Session

class CronScheduler(Component):
    def __init__(self, core):
        super(CronScheduler, self).__init__(core)
        self.callback = PeriodicCallback(self.run, options.cron_interval * 1000)

    def run(self):
        logging.info("Running cron...")

        cursor = meta.session.find(Session, {
            "last_active" :
            {
                "$lte" : datetime.utcnow() - timedelta(seconds=options.session_expiry)
            }
        })
        num_rows = cursor.count()

        for session in cursor:
            if session.token in self.core.connections:
                self.core.connections[session.token].shutdown("Heartbeat timeout")
                logging.info("Dropped active connection %s." % session.token)
            meta.session.remove(Session, { "_id" : session._id })

        logging.info("Purged %d expired session(s)." % num_rows)

    def go(self):
        self.run()
        self.callback.start()
