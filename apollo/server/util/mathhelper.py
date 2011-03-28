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
Various mathematical utilities.
"""

from math import pi, sin, cos, sqrt

PI = pi
"""
O glorious pi.
"""

TAU = pi * 2.0
"""
The number that is numerically twice of pi and philosophically much more!

http://tauday.com
"""

TAU_OVER_EIGHT = pi / 4.0
"""
Just the number tau divided by 8.
"""

SCALING_CONSTANT = 1 / sqrt(2)
"""
Constant for scaling tiles into isometric display.
"""

def isometricTransform(x, y):
    """
    Transform Cartesian coordinates to isometric coordinates in Cartesian space.

    This is the simplified form of a matrix multiplication or complex number
    spiral enlargement that scales by ``SCALING_CONSTANT`` and rotates by
    ``TAU_OVER_EIGHT``.
    """
    return (
        (x - y) / 2.0,
        (x + y) / 2.0
    )

def absolve(x, y, s):
    """
    Resolve absolute coordinates into chunk and relative coordinates.

    :Parameters:
         * ``x``
           Absolute x coordinate.

         * ``y``
           Absolute y coordinate.

         * ``s``
           Chunk stride.

   :Returns:
        A tuple containing the chunk coordinates and a tuple containing the
        relative coordinates, in that order.
    """
    return (x // s, y // s), (x % s, y % s)

def dissolve(cx, cy, rx, ry, s):
    """
    Dissolve chunk and relative coordinates into absolute coordinates.

    :Parameters:
         * ``cx``
           Chunk x coordinate.

         * ``cy``
           Chunk y coordinate.

         * ``rx``
           Relative x coordinate.

         * ``ry``
           Relative y coordinate.

         * ``s``
           Chunk stride.

   :Returns:
        A tuple containing absolute coordinates.
    """
    return (cx * s + rx, cy * s + ry)