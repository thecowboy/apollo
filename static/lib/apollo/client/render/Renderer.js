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

dojo.provide("apollo.client.render.Renderer");

dojo.require("apollo.client.Component");
dojo.require("apollo.client.util.mathhelper");

dojo.declare("apollo.client.render.Renderer", apollo.client.Component, {
    CHUNK_STRIDE : 8,
    TILE_HEIGHT : 32,
    TILE_WIDTH : 64,

    constructor : function(core)
    {
        this.chunkCache = {};
        this.canvas = dojo.byId("surface");
        this.redraw = function() { };
        this.autofit();

        dojo.connect(window, "onresize", dojo.hitch(this, function()
        {
            this.autofit();
        }));
    },

    autofit : function()
    {
        var pos = dojo.position("gameSurface");
        this.canvas.width = pos.w;
        this.canvas.height = pos.h;
        this.redraw();
    },

    getUnixTimestamp : function()
    {
        return Math.floor((new Date()).getTime() / 1000);
    },

    draw : function(pos, size)
    {
        // first, resolve the position into chunk coordinates
        var ccoords = {
            x : Math.floor(pos.x / this.CHUNK_STRIDE),
            y : Math.floor(pos.y / this.CHUNK_STRIDE)
        };

        // extract the relative position data
        var rcoords = {
            x : pos.x % this.CHUNK_STRIDE,
            y : pos.y % this.CHUNK_STRIDE
        };

        for(var cx = 0; cx < 3; ++cx)
        {
            for(var cy = 0; cy < 3; ++cy)
            {
                var tcoords = apollo.client.util.mathhelper.isometricTransform(
                    (cx - ccoords.x) * this.CHUNK_STRIDE - rcoords.x,
                    (cy - ccoords.y) * this.CHUNK_STRIDE - rcoords.y
                );

                // now draw the chunks
                if(this.chunkCache[cx + "." + cy] == undefined)
                {
                    var img;

                    this.chunkCache[cx + "." + cy] = img = new Image();
                    dojo.connect(img, "onload", dojo.hitch(this, function()
                    {
                        this.chunkDrawCallback(img, tcoords, rcoords);
                    }));
                    img.src = "static/chunks/" + cx + "." + cy + ".png?" + this.getUnixTimestamp();
                } else {
                    this.chunkDrawCallback(this.chunkCache[cx + "." + cy], tcoords, rcoords);
                }
            }
        }

        // now make a redraw function (partial application)
        this.redraw = function() { this.draw(pos, size); }
    },

    chunkDrawCallback : function(img, coords)
    {
        var CHUNK_HEIGHT = this.CHUNK_STRIDE * this.TILE_HEIGHT;
        var CHUNK_WIDTH = this.CHUNK_STRIDE * this.TILE_WIDTH;

        var ctx = this.canvas.getContext("2d");
        console.log(coords);
        ctx.drawImage(
            img,
            Math.round(coords.x * this.TILE_WIDTH + this.canvas.width / 2 - CHUNK_WIDTH / 2),
            Math.round(coords.y * this.TILE_HEIGHT + this.canvas.height / 2 - this.TILE_HEIGHT)
        );
    },

    clobber : function(cx, cy)
    {
        if(this.chunkCache[cx + "." + cy]) delete this.chunkCache[cx + "." + cy];
    }
});
