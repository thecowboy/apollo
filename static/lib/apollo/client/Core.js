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

dojo.provide("apollo.client.Core");

dojo.require("apollo.client.ActionDispatcher");
dojo.require("apollo.client.render.Renderer");
dojo.require("apollo.client.protocol.Transport");

dojo.require("apollo.client.protocol.packet.PacketUser");
dojo.require("apollo.client.protocol.packet.PacketInfo");

dojo.declare("apollo.client.Core", null, {
    constructor : function()
    {
        this.transport = new apollo.client.protocol.Transport(this);
        this.renderer = new apollo.client.render.Renderer(this);
        this.actions = new apollo.client.ActionDispatcher(this.transport);
    },

    auth : function()
    {
        dijit.byId("loginDialog").hide();
        this.requery();
    },

    requery : function()
    {
        this.transport.sendAction(new apollo.client.protocol.packet.PacketUser());
        this.transport.sendAction(new apollo.client.protocol.packet.PacketInfo());
    },

    deauth : function(msg)
    {
        dojo.byId("logoutReason").innerHTML = msg;
        dijit.byId("logoutDialog").show();
        this.dead = true;
        this.transport.shutdown();
    },

    ready : function()
    {
        dijit.byId("loadingDialog").hide();
        dijit.byId("loginDialog").show();
    },

    go : function()
    {
        dijit.byId("loadingDialog").show();
        this.transport.go();
    },

    die : function(msg)
    {
        if(this.dead) return;

        this.dead = true;

        dojo.byId("errorMessage").innerHTML = msg;
        dijit.byId("errorDialog").show();

        this.transport.shutdown();
    }
});
