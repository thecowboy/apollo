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

dojo.require("apollo.client.protocol.packet.PacketHeartbeat");
dojo.require("apollo.client.protocol.packet.PacketError");

dojo.require("apollo.client.dylib.packetlist");
dojo.require("apollo.client.dylib.config");

dojo.declare("apollo.client.protocol.Transport", apollo.client.Component, {
    eventComet : function()
    {
        dojo.xhrGet({
            url         : "events",
            content     : {
                s       : this.token
            },
            handleAs    : "json",
            load        : dojo.hitch(this, function(packet)
            {
                // do stuff
                try
                {
                    this.processEvent(packet);
                } catch(e) {
                    core.die("Internal error (transport event): " + e);
                    throw e;
                }

                // start the comet loop again (if we want to)
                if(!this.shutdowned)
                {
                    this.eventComet();
                }
            }),
            error       : function(e)
            {
                core.die("Transport error (event): " + e);
            }
        });
    },

    processEvent : function(packet)
    {
        var packetType = apollo.client.dylib.packetlist[packet._name];

        if(packetType)
        {
            (new packetType(packet)).dispatch(this, this.core);
        }
    },

    sendAction : function(packet)
    {
        dojo.xhrPost({
            url         : "action",
            content     : {
                p       : packet.dump(),
                s       : this.token
            },
            handleAs    : "text",
            error       : function(e)
            {
                core.die("Transport error (action): " + e);
            }
        });
    },

    acquireSession : function()
    {
        dojo.xhrGet({
            url         : "session",
            handleAs    : "json",
            load        : dojo.hitch(this, function(packet)
            {
                this.token = packet.s;

                this.core.ready();
                this.startHeartbeat();

                // start 4 event comet streams
                this.eventComet();
                this.eventComet();
                this.eventComet();
                this.eventComet();
            }),
            error       : function(e)
            {
                core.die("Session acquisition error: " + e);
            }
        });
    },

    go : function()
    {
        this.acquireSession();
    },

    startHeartbeat : function()
    {
        this.heartbeat = setInterval(dojo.hitch(this, function()
        {
            this.sendAction(new apollo.client.protocol.packet.PacketHeartbeat());
        }), apollo.client.dylib.config.session_expiry * 1000 / 30);
    },

    stopHeartbeat : function()
    {
        clearInterval(this.heartbeat);
    },

    shutdown : function()
    {
        this.shutdowned = true;
        this.stopHeartbeat();
    }
});
