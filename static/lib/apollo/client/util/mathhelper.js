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
 
apollo.client.util.mathhelper.PI = PI = Math.PI;

apollo.client.util.mathhelper.TAU = TAU = PI * 2;

apollo.client.util.mathhelper.TAU_OVER_EIGHT = TAU_OVER_EIGHT = Math.PI / 4;

apollo.client.util.mathhelper.SCALING_CONSTANT = SCALING_CONSTANT = 1 / Math.sqrt(2);

apollo.client.util.mathhelper.isometricTransform = function(x, y)
{
    return {
        x: (x - y) / 2,
        y: (x + y) / 2
    };
};

apollo.client.util.mathhelper.cartesianTransform = function(x, y)
{
    return {
        x: x + y,
        y: y - x
    };
};

apollo.client.util.mathhelper.clamp = function(val, min, max)
{
    return Math.max(Math.min(val, max), min);
};


apollo.client.util.mathhelper.hypot = function(x, y)
{
    return Math.sqrt(x * x + y * y);
};

apollo.client.util.mathhelper.absolve = function(x, y, s) // absolute coordinate resolution
{
    return {
        r : { // relative
            x : x % s,
            y : y % s
        },

        c : { // chunk
            x : Math.floor(x / s),
            y : Math.floor(y / s)
        }
    }
};
