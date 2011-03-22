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
from numpy import matrix
from numpy.linalg import inv

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

CARTESIAN_TO_ISOMETRIC_MATRIX = matrix([
    [SCALING_CONSTANT, 0 ],                         # shrink vertically to scale
    [0, SCALING_CONSTANT ]
]) * matrix([
    [cos(TAU_OVER_EIGHT), -sin(TAU_OVER_EIGHT)],    # do a 45 degree rotation
    [sin(TAU_OVER_EIGHT),  cos(TAU_OVER_EIGHT)]
])
"""
Matrix for converting Cartesian coordinates to isometric in Cartesian space.
Does not perform any translations.
"""

ISOMETRIC_TO_CARTESIAN_MATRIX = inv(CARTESIAN_TO_ISOMETRIC_MATRIX)
"""
Matrix for converting isometric coordinates in Cartesian space back to
Cartesian coordinates.
"""

def isometricTransform(x, y):
    """
    Transform Cartesian coordinates to isometric coordinates in Cartesian space
    using ``CARTESIAN_TO_ISOMETRIC_MATRIX``.
    """
    transformed_vec = CARTESIAN_TO_ISOMETRIC_MATRIX * matrix([[x],[y]])
    return (
        transformed_vec[0, 0],
        transformed_vec[1, 0]
    )
