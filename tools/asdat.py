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
Apollo security domain administration tool.
"""

import sys
import os

dist_root = os.path.join(os.path.dirname(__file__), "..")

# add the apollo path to the pythonpath
sys.path.insert(1, dist_root)

from apollo.server import skeletonSetup
from apollo.server.models import meta
from apollo.server.models.auth import SecurityDomain

def printDomainTree(domain, level=0):
    sess = meta.Session()

    print "| %s%s" % ("    " * level, domain.name)

    for domain in sess.query(SecurityDomain).filter(SecurityDomain.parent_id == domain.id):
        printDomainTree(domain, level+1)

if __name__ == "__main__":
    skeletonSetup(os.path.join(dist_root, "apollod.conf"))

    print "Apollo Security Domain Administration Tool\n"

    sess = meta.Session()

    for domain in sess.query(SecurityDomain).filter(SecurityDomain.parent_id == None):
        print "Tree:"
        printDomainTree(domain)
