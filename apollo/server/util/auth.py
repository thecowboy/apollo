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

from apollo.server.models.auth import SecurityDomain
from apollo.server.protocol.packet.packeterror import PacketError, SEVERITY_WARN

def requireAuthorization(domain_path):
    """
    Dispatch the packet only if the user is part of a security domain.

    :Parameters:
        * ``domain_path``
          Path to the domain.
    """
    def _decorator(fn):
        @wraps(fn)
        def _closure(self, core, session):
            if not hasattr(fn, "apollo_securityDomain"):
                fn.apollo_securityDomain = SecurityDomain.byPath(domain_path)

            user = session.user
            if user.inDomain(fn.apollo_securityDomain):
                fn(self, core, session)
            else:
                user.sendEx(core.bus, PacketError(severity=SEVERITY_WARN, msg="Not permitted to perform action."))
        return _closure
    return _decorator

def requireAuthentication(fn):
    """
    Dispatch the packet only if logged in.
    """
    @wraps(fn)
    def _closure(self, core, session):
        if session.user is None:
            session.sendEx(core.bus, PacketError(msg="not authenticated"))
        else:
            fn(self, core, session)
    return _closure
