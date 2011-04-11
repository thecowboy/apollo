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

__name__ = "Hooks"
__author__ = "Tony Young"
__version__ = "0.1"
__description__ = "Mechanism to hook various events via monkey patching."

class HookRegistry(object):
    def __init__(self):
        self.registry = {}

    def registerHook(self, hook):
        self.registry[hook.name] = hook
        return hook

    def __getattr__(self, item):
        return self.registry[item]

class Hook(object):
    def __init__(self, name):
        self.name = name
        self.listeners = []

    def addListener(self, listener):
        self.listeners.append(listener)

    def removeListener(self, listener):
        self.listeners.remove(listener)

    def __call__(self, *args, **kwargs):
        for listener in self.listeners:
            listener(*args, **kwargs)

def setup(*args):
    globals()["registry"] = HookRegistry()

    from apollo.server.protocol.packet.packetmove import PacketMove

    # hooks for PacketMove
    before_move = registry.registerHook(Hook("before_move"))
    after_move = registry.registerHook(Hook("after_move"))

    def monkey_PacketMove(fn):
        def dispatch(self, core, session):
            before_move(self, core, session)
            if fn(self, core, session):
                after_move(self, core, session)
        return dispatch

    PacketMove.dispatch = monkey_PacketMove(PacketMove.dispatch)
