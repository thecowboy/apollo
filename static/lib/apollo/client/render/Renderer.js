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
        this.autofit();

        dojo.connect(window, "onresize", dojo.hitch(this, function()
        {
            this.autofit();
        }));

        this.redraw = function() { };
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

        // now draw the current chunk
        if(this.chunkCache[ccoords] == undefined)
        {
            var img;
            var that = this;

            this.chunkCache[ccoords.x + "," + ccoords.y] = img = new Image();
            dojo.connect(img, "onload", function()
            {
                this.loaded = true;
                that.chunkDrawCallback(img, rcoords);
            });
            img.src = "static/chunks/" + ccoords.x + "." + ccoords.y + ".png?" + this.getUnixTimestamp();
        } else {
            this.chunkDrawCallback(this.chunkCache[ccoords.x + "," + ccoords.y], rcoords);
        }

        // now make a redraw function (partial application)
        this.redraw = function() { this.draw(pos, size); }
    },

    chunkDrawCallback : function(img, rcoords)
    {
        var ctx = this.canvas.getContext("2d");
        ctx.drawImage(
            img,
            this.canvas.width / 2 - (rcoords.x + 1) * this.TILE_WIDTH,
            this.canvas.height / 2 - (rcoords.y + 0.5) * this.TILE_HEIGHT
        );
    },

    clobber : function(cx, cy)
    {
        if(this.chunkCache[cx + "," + cy]) delete this.chunkCache[cx + "," + cy];
    }
});
