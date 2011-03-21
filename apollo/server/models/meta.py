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

# I stole this idea from Pylons

import os

from apollo.server.util.importlib import import_module

from ming import Session
from ming.orm import MappedClass
from ming.orm import ThreadLocalORMSession

doc_session = Session()
session = ThreadLocalORMSession(doc_session=doc_session)

def bind_session(bind):
    """
    Bind the session to a database connection.

    :Parameters:
         * ``bind``
            Database connection.
    """
    doc_session.bind = bind
    autodiscover()

def autodiscover():
    """
    Autodiscover all models and compile them.
    """
    for filename in os.listdir(os.path.dirname(__file__)):
        if filename[-3:] == ".py":
            module_name, ext = filename.rsplit(".", 1)

            if module_name in ("meta", "__init__"):
                continue

            module = import_module(".%s" % module_name, "apollo.server.models")
            for member_name in dir(module):
                member = getattr(module, member_name)
                if isinstance(member, MappedClass):
                    locals()[member.__name__] = member

    MappedClass.compile_all()
