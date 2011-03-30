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

import json

ORIGIN_EX = 1
ORIGIN_INTER = 2

class Packet(object):
    """
    Base packet class. Implements the command pattern.
    """
    def __init__(self, **payload):
        self.__dict__.update(payload)

    def dispatch(self, core, session):
        """
        Dispatch the packet. Can be decorated with decorators from
        ``apollo.server.util.decorators``.

        :Parameters:
            * ``core``
              The Core object.

            * ``session``
              The session processing the packet.
        """
        pass

    def dump(self):
        """
        Dump the packet into JSON format.
        """
        dic = self.__dict__.copy()
        dic["__name__"] = self.__class__.name
        return json.dumps(dic)

    def __getattr__(self, attr):
        return None

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.dump())
