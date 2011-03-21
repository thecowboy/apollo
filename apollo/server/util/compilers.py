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
Compilers for database code.
"""

class BaseCompiler(object):
    """
    Base compiler class. Subclasses should override the ``compile`` method.
    """
    cache = {}

    def __init__(self, code):
        """
        Initialize a compiler.

        :Parameter:
            * ``code``
              Code to compile.
        """
        if (self.__class__.__name__, code) not in self.cache:
            self.cache[self.__class__.__name__, code] = self.compile(code)

        self.code_obj = self.cache[self.__class__.__name__, code]

    def compile(self, code):
        """
        Implementation for compiler that returns a code objcet.

        :Parameter:
            * ``code``
              Code to compile.
        """
        raise NotImplementedError

    def __call__(self, **locals):
        return eval(self.code_obj, locals)

class CurveCompiler(BaseCompiler):
    """
    Compile a stat curve expression, e.g. ``profession.hpcurve``.
    """
    def compile(self, code):
        return compile(
            code,
            "<curve mapping: %s>" % code,
            "eval"
        )

class EventCompiler(BaseCompiler):
    """
    Compile event code.
    """
    def compile(self, code):
        return compile(
            code,
            "<event code>",
            "exec"
        )
