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
Apollo server authorization and authentication decorators.
"""

from functools import wraps

from apollo.server.protocol.packet.packeterror import PacketError, SEVERITY_WARN

def requirePermission(permission):
    """
    Dispatch the packet only if a specific permission is present.

    :Parameters:
        * ``permission``
          Permission required.
    """
    def _decorator(fn):
        @wraps(fn)
        def _closure(self, core, session):
            user = session.getUser()
            if user.hasPermission(permission):
                fn(self, core, session)
            else:
                core.bus.broadcast("ex.user.%s" % user._id, PacketError(severity=SEVERITY_WARN, msg="Not permitted to perform action."))
        return _closure
    return _decorator

def requireAuthentication(fn):
    """
    Dispatch the packet only if logged in.
    """
    @wraps(fn)
    def _closure(self, core, session):
        try:
            user = session.getUser()
        except ValueError:
            core.bus.broadcast("ex.session.%s" % session._id, PacketError(msg="not authenticated"))
        else:
            fn(self, core, session)
    return _closure