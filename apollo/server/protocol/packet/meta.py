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

from apollo.server.util.importlib import import_module

import os
import json

packetlist = {}

def autodiscover():
    """
    Autodiscover all packets and store them in the packet list.
    """
    for filename in os.listdir(os.path.dirname(__file__)):
        if filename[-3:] == ".py":
            # assume this is a packet
            module_name, ext = filename.rsplit(".", 1)

            if module_name[:6] != "packet":
                continue

            module = import_module(".%s" % module_name, "apollo.server.protocol.packet")
            for member_name in dir(module):
                if member_name != "Packet" and member_name[:6] == "Packet":
                    member = getattr(module, member_name)
                    packetlist[member.name] = member

autodiscover()

def deserializePacket(payload):
    """
    Deserialize a packet into the appropriate packet object.

    :Parameters:
         * ``payload``
           Packet payload that was transferred.
    """
    depayload = json.loads(payload)
    name = depayload.get("__name__")
    if name in packetlist:
        return packetlist[name](**depayload)
