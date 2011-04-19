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

from tornado.ioloop import PeriodicCallback

from apollo.server.component import Component

from apollo.server.models import meta
from apollo.server.models.auth import Session, User
from apollo.server.protocol.packet.packetlogout import PacketLogout

class CronScheduler(Component):
    """
    Apollo scheduler service. Performs clean up of dead sessions, etc.
    """
    def run(self):
        """
        Run cron (once).
        """
        sess = meta.Session()

        if not self.core.bus.ready:
            logging.warn("Bus is not ready, not running cron.")
            return

        logging.info("Running cron...")

        cursor = sess.query(Session).filter(Session.last_active <= datetime.utcnow() - timedelta(seconds=options.session_expiry))
        num_rows = cursor.count()

        for session in cursor:
            user = sess.query(User).get(session.user_id)
            if user is not None:
                if user.online:
                    user.sendInter(self.core.bus, PacketLogout(msg="Heartbeat timeout"))
                user.online = False
                sess.merge(user)

        cursor.delete()
        sess.commit()
        logging.info("Purged %d expired session(s)." % num_rows)

    def go(self):
        """
        Start the cron cycle.
        """
        self.callback = PeriodicCallback(self.run, options.cron_interval * 1000)
        self.callback.start()
