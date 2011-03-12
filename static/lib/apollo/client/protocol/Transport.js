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

dojo.provide("apollo.client.protocol.Transport");

dojo.require("apollo.client.Component");
dojo.require("apollo.client.dylib.packetlist");
dojo.require("apollo.client.protocol.packet.PacketError");

dojo.declare("apollo.client.protocol.Transport", apollo.client.Component, {
    constructor : function(core)
    {
        var that = this;

        this.actionAjax = {
            url         : "action",
            handleAs    : "json",
            load        : function(packet)
            {
                // do stuff
                that.processActionResult(packet);
            }
        };

        this.eventComet = {
            url         : "events",
            handleAs    : "json",
            load        : function(packet)
            {
                // do stuff
                that.processEvent(packet);

                // start the comet loop again
                that.eventComet();
            }
        };
    },

    eventComet : function()
    {
        dojo.xhrGet(this.cometArgs);
    },

    processActionResult : function(packet)
    {
    },

    processEvent : function(packet)
    {
        var packetType = apollo.client.dylib.packetlist[packet.name];

        if(packetType)
        {
            dojo.safeMixin(new packetType(this, this.core), packet.payload).dispatch();
        } else {
            this.sendAction(new apollo.client.protocol.packet.PacketError(this, this.core));
        }
    },

    sendAction : function(packet)
    {
        var encapsulatedPacket = {
            name        : packet.name,
            payload     : packet
        };
        dojo.xhrPost(dojo.safeMixin(this.actionAjax, {
            postdata : "p=" + escape(JSON.stringify(encapsulatedPacket))
        }));
    },

    go : function()
    {
    },
});
