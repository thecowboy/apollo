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
    eventComet : function()
    {
        var that = this;

        dojo.xhrGet({
            url         : "events?s=" + escape(this.sessionId),
            handleAs    : "json",
            load        : function(packet)
            {
                // do stuff
                that.processEvent(packet);

                // start the comet loop again
                that.eventComet();
            }
        });
    },

    processEvent : function(packet)
    {
        var packetType = apollo.client.dylib.packetlist[packet.name];

        if(packetType)
        {
            (new packetType(packet.payload)).dispatch(this, this.core);
        }
    },

    sendAction : function(packet)
    {
        var that = this;

        dojo.xhrPost({
            url         : "action",
            handleAs    : "text",
            postData    : "p=" + escape(packet.dump()) + "&s=" + that.sessionId
        });
    },

    go : function()
    {
        var that = this;

        dojo.xhrGet({
            url         : "session",
            handleAs    : "text",
            load        : function(sessionId)
            {
                that.sessionId = sessionId;
                that.eventComet();
            }
        });
    },
});
