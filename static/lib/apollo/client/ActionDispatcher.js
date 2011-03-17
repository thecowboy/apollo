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

dojo.provide("apollo.client.ActionDispatcher");

dojo.require("apollo.client.util.sha256");

// packets
dojo.require("apollo.client.protocol.packet.PacketLogin");
dojo.require("apollo.client.protocol.packet.PacketLogout");
dojo.require("apollo.client.protocol.packet.PacketChat");

dojo.declare("apollo.client.ActionDispatcher", null, {
    constructor : function(transport)
    {
        this.transport = transport;
    },

    login : function(username, password)
    {
        var nonce = apollo.client.util.sha256.sha256(Math.random() + "" + Math.random() + "" + Math.random());

        this.transport.sendAction(new apollo.client.protocol.packet.PacketLogin({
            username    : username,
            pwhash      : apollo.client.util.sha256.sha256(
                nonce +
                apollo.client.util.sha256.sha256(
                    username.toLowerCase() + ":" + password
                ) +
                this.transport.nonce
            ),
            nonce       : nonce
        }));
    },

    logout : function()
    {
        this.transport.sendAction(new apollo.client.protocol.packet.PacketLogout());
    },

    chat : function(msg)
    {
        this.transport.sendAction(new apollo.client.protocol.packet.PacketChat({ msg: msg }));
    },
});
