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

from types import MethodType

class PredicateNotMatchedError(Exception):
    """
    An error thrown when a ``predicated`` is invoked when its predicate is not
    true.
    """
    pass

class predicated(object):
    """
    Represents an function requiring a certain criteria to be met before being
    allowed to run.
    """

    def __init__(self, fn):
        self.fn = fn
        self.fpred = lambda *args, **kwargs: True

    def predicate(self, predicate):
        self.fpred = predicate
        return self

    def validate(self, *args, **kwargs):
        return self.fpred(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if not self.validate(*args, **kwargs):
            raise PredicateNotMatchedError("predicate was not matched")
        return self.fn(*args, **kwargs)

    def __get__(self, obj, objtype=None):
        return MethodType(self, obj, objtype)
