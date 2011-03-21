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
Dylib dispatching and autodiscovery.
"""

from apollo.server.component import Component
from apollo.server.util.importlib import import_module

import os

class DylibDispatcher(Component):
    """
    Dispatcher for dylibs. Handles requests for them.
    """

    def __init__(self, core):
        super(DylibDispatcher, self).__init__(core)
        self.dylibs = {}

        self.autodiscover()

    def autodiscover(self):
        """
        Autodiscover all dylibs. The following conditions must hold for a dylib
        to be autodiscovered:

         * Its filename must begin with ``dylib`` and end with ``.py``.
        
         * It must have a member that begins with ``Dylib``.
        """
        for filename in os.listdir(os.path.dirname(__file__)):
            if filename[-3:] == ".py":
                module_name, ext = filename.rsplit(".", 1)

                # do not scan if it does not start with dylib
                if module_name[:5] != "dylib":
                    continue

                module = import_module(".%s" % module_name, "apollo.server.dylib")
                for member_name in dir(module):
                    if member_name != "Dylib" and member_name[:5] == "Dylib":
                        member = getattr(module, member_name)
                        self.dylibs[member.name] = member(self.core)

    def dispatch(self, pathspec):
        """
        Dispatch a dylib request according to a path specification.

        :Parameters:
            * ``pathspec``
              Path specification.
        """
        if pathspec in self.dylibs:
            return self.dylibs[pathspec].generate()
        return None
