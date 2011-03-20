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

from apollo.server.protocol.packet import Packet

from apollo.server.models import meta
from apollo.server.models.profession import Profession

from apollo.server.util.decorators import requireAuthentication
from apollo.server.util.compilers import CurveCompiler

class PacketUser(Packet):
    name = "user"

    @requireAuthentication
    def dispatch(self, transport, core):
        user = transport.session().getUser()
        profession = meta.session.get(Profession, user.profession_id)

        transport.sendEvent(PacketUser(
            name=user.name,
            level=user.level,
            hp={ "now" : user.hp, "max" : CurveCompiler(profession.hpcurve)(user=user) },
            ap={ "now" : user.ap, "max" : CurveCompiler(profession.apcurve)(user=user) },
            xp={ "now" : user.xp, "max" : CurveCompiler(profession.xpcurve)(user=user) }
        ))