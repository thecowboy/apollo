/*
 * Copyright (C) 2011 by Tony Young
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */

dojo.provide("apollo.client.util.mathhelper");
 
dojo.require("dojox.gfx.matrix");

apollo.client.util.mathhelper.PI = PI = Math.PI;

apollo.client.util.mathhelper.TAU = TAU = PI * 2;

apollo.client.util.mathhelper.TAU_OVER_EIGHT = TAU_OVER_EIGHT = Math.PI / 4;

apollo.client.util.mathhelper.SCALING_CONSTANT = SCALING_CONSTANT = 1 / Math.sqrt(2);

apollo.client.util.mathhelper.CARTESIAN_TO_ISOMETRIC_MATRIX = CARTESIAN_TO_ISOMETRIC_MATRIX = dojox.gfx.matrix.multiply
(
    new dojox.gfx.matrix.Matrix2D({
        xx : SCALING_CONSTANT, xy: 0,
        yx : 0,                yy: SCALING_CONSTANT
    }),
    new dojox.gfx.matrix.Matrix2D({
        xx : Math.cos(TAU_OVER_EIGHT), xy: -Math.sin(TAU_OVER_EIGHT),
        yx : Math.sin(TAU_OVER_EIGHT), yy: Math.cos(TAU_OVER_EIGHT)
    })
);

apollo.client.util.mathhelper.ISOMETRIC_TO_CARTESIAN_MATRIX = ISOMETRIC_TO_CARTESIAN_MATRIX = dojox.gfx.matrix.invert(CARTESIAN_TO_ISOMETRIC_MATRIX);

apollo.client.util.mathhelper.isometricTransform = function(x, y)
{
    var vec = dojox.gfx.matrix.multiplyPoint(CARTESIAN_TO_ISOMETRIC_MATRIX, x, y);
    return {
        x: vec.x,
        y: vec.y
    };
}

apollo.client.util.mathhelper.cartesianTransform = function(x, y)
{
    var vec = dojox.gfx.matrix.multiplyPoint(ISOMETRIC_TO_CARTESIAN_MATRIX, x, y);
    return {
        x: vec.x,
        y: vec.y
    };
}

apollo.client.util.mathhelper.clamp = function(val, min, max)
{
    return Math.max(Math.min(val, max), min);
}
