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

dojo.require("apollo.client.protocol.packet.PacketMove");

var CHUNK_STRIDE = 8;
var TILE_HEIGHT = 32;
var TILE_WIDTH = 64;

var CHUNK_HEIGHT = CHUNK_STRIDE * TILE_HEIGHT;
var CHUNK_WIDTH = CHUNK_STRIDE * TILE_WIDTH;

dojo.declare("apollo.client.render.Renderer", apollo.client.Component, {
    CHUNK_STRIDE : CHUNK_STRIDE,
    TILE_HEIGHT : TILE_HEIGHT,
    TILE_WIDTH : TILE_WIDTH,

    CHUNK_HEIGHT : CHUNK_HEIGHT,
    CHUNK_WIDTH : CHUNK_WIDTH,

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

        dojo.connect(this.canvas, "onmousemove", dojo.hitch(this, this.handleMouseMove));
        dojo.connect(this.canvas, "onmouseout", dojo.hitch(this, this.redraw));
    },

    autofit : function()
    {
        var pos = dojo.position("gameSurface");
        this.canvas.width = pos.w;
        this.canvas.height = pos.h;
        this.context = this.canvas.getContext("2d");
        this.redraw();
    },

    getUnixTimestamp : function()
    {
        return Math.floor((new Date()).getTime() / 1000);
    },

    transformToIsometric : function(x, y)
    {
        // calculate the coordinates in terms isometric map coordinates (normalize first)
        var isocoords = {
            x : (x + this.CHUNK_WIDTH / 2 - this.canvas.width / 2) / this.TILE_WIDTH,
            y : (y + this.TILE_HEIGHT / 2 - this.canvas.height / 2) / this.TILE_HEIGHT
        };

        isocoords = apollo.client.util.mathhelper.cartesianTransform(isocoords.x, isocoords.y);

        // finally round it off
        isocoords = {
            x : Math.round(isocoords.x + 0.5),
            y : Math.round(isocoords.y + 0.5)
        };

        // XXX: why are the numbers 5 and -3 required ? probably something wrong
        //      with my math :(
        return {
            x : isocoords.x - 5,
            y : isocoords.y + 3
        };
    },

    handleClick : function(pos, size, evt)
    {
        var canvaspos = dojo.position(this.canvas);

        var tpos = this.transformToIsometric(
            evt.clientX - canvaspos.x,
            evt.clientY - canvaspos.y
        );

        var realpos = {
            x : tpos.x + pos.x,
            y : tpos.y + pos.y
        };

        // don't allow clicking outside the map (server will eat this anyway)
        if(
            realpos.x < 0 || realpos.x >= size.cw * this.CHUNK_STRIDE ||
            realpos.y < 0 || realpos.y >= size.ch * this.CHUNK_STRIDE
        ) return;

        this.core.transport.sendAction(new apollo.client.protocol.packet.PacketMove(realpos));
    },

    handleMouseMove : function(evt)
    {
        this.redraw();

        var canvaspos = dojo.position(this.canvas);

        var tpos = this.transformToIsometric(
            evt.clientX - canvaspos.x,
            evt.clientY - canvaspos.y
        );

        var backtpos = apollo.client.util.mathhelper.isometricTransform(
            tpos.x,
            tpos.y
        );

        var realpos = {
            x : Math.round(backtpos.x * this.TILE_WIDTH + canvaspos.w / 2),
            y : Math.round(backtpos.y * this.TILE_HEIGHT + canvaspos.h / 2)
        };

        this.context.save();
        this.context.fillStyle = "rgba(0, 0, 0, 0.5)";
        this.context.beginPath();
        this.context.moveTo(realpos.x - this.TILE_WIDTH / 2, realpos.y);
        this.context.lineTo(realpos.x, realpos.y - this.TILE_HEIGHT / 2);
        this.context.lineTo(realpos.x + this.TILE_WIDTH / 2, realpos.y);
        this.context.lineTo(realpos.x, realpos.y + this.TILE_HEIGHT / 2);
        this.context.closePath();
        this.context.fill();
        this.context.restore();
    },

    draw : function(pos, size)
    {
        var surfdim = dojo.position("gameSurface");

        // clear the screen
        this.context.clearRect(0, 0, surfdim.w, surfdim.h);

        // resolve coordinates
        var rcoords = apollo.client.util.mathhelper.absolve(pos.x, pos.y, this.CHUNK_STRIDE);

        // chunk limit coordinates
        var lcoords = apollo.client.util.mathhelper.cartesianTransform(
            this.canvas.width / this.CHUNK_WIDTH,
            this.canvas.height / this.CHUNK_HEIGHT
        );

        // number of chunks that need to be rendered (first pass)
        var drawlength = Math.ceil(apollo.client.util.mathhelper.hypot(lcoords.x, lcoords.y));

        for(
            var cx = Math.floor(apollo.client.util.mathhelper.clamp((rcoords.c.x - drawlength / 2), 0, size.cw - 1));
            cx <= Math.ceil(apollo.client.util.mathhelper.clamp((rcoords.c.x + drawlength / 2), 0, size.cw - 1));
            ++cx
        )
        {
            for(
                var cy = Math.floor(apollo.client.util.mathhelper.clamp((rcoords.c.y - drawlength / 2), 0, size.ch - 1));
                cy <= Math.ceil(apollo.client.util.mathhelper.clamp((rcoords.c.y + drawlength / 2), 0, size.ch - 1));
                ++cy
            )
            {
                var tcoords = apollo.client.util.mathhelper.isometricTransform(
                    (cx - rcoords.c.x) * this.CHUNK_STRIDE - rcoords.r.x,
                    (cy - rcoords.c.y) * this.CHUNK_STRIDE - rcoords.r.y
                );

                tcoords = {
                    x: Math.round(tcoords.x * this.TILE_WIDTH + this.canvas.width / 2 - this.CHUNK_WIDTH / 2),
                    y: Math.round(tcoords.y * this.TILE_HEIGHT + this.canvas.height / 2 - this.TILE_HEIGHT / 2)
                };

                // cull chunks that lie outside of screen space (second pass)
                if(
                    tcoords.x < -this.CHUNK_WIDTH || tcoords.x > this.canvas.width ||
                    tcoords.y < -this.CHUNK_HEIGHT || tcoords.y > this.canvas.height
                ) continue;

                var img = this.chunkCache[cx + "." + cy];

                // now draw the chunks
                if(img == undefined)
                {
                    var that = this;
                    this.chunkCache[cx + "." + cy] = img = new Image();

                    // why is dojo.partial required below?
                    // see: http://stackoverflow.com/questions/3258930/drawing-multiple-images-to-a-canvas-using-image-onload
                    //
                    // basically, if tcoords is used directly, a reference to it
                    // is passed rather than the value.
                    //
                    // to get around this, a closure is made (with dojo.partial)
                    // to make it less retarded.
                    dojo.connect(img, "onload", dojo.partial(function(tcoords)
                    {
                        that.context.drawImage(this, tcoords.x, tcoords.y);
                    }, tcoords));
                    img.src = "static/chunks/" + cx + "." + cy + ".png?" + this.getUnixTimestamp();
                } else {
                    this.context.drawImage(img, tcoords.x, tcoords.y);
                }
            }
        }

        // now make a redraw function (partial application)
        this.redraw = dojo.partial(this.draw, pos, size);

        // and reconnect onclick
        if(this.clickHandle) dojo.disconnect(this.clickHandle);
        this.clickHandle = dojo.connect(this.canvas, "onclick", dojo.hitch(this, dojo.partial(this.handleClick, pos, size)));
    },

    clobber : function(cx, cy)
    {
        if(this.chunkCache[cx + "." + cy]) delete this.chunkCache[cx + "." + cy];
    }
});
