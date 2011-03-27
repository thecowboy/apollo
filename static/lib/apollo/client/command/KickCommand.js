/*
 * Copyright (C) 2011 by Ryan Lewis
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

dojo.provide("apollo.client.command.KickCommand");

dojo.require("apollo.client.protocol.packet.PacketKick");

dojo.require("apollo.client.util.ui");

dojo.require("apollo.client.command.Command");

dojo.declare("apollo.client.command.KickCommand", apollo.client.command.Command, {
    execute : function(transport)
    {
        var rest = Array.prototype.splice.call(arguments, 1);
        if (rest.length < 1)
        {
            apollo.client.util.ui.addConsoleMessage("Incorrect number of arguments.");
            return;
        }
        transport.sendAction(new apollo.client.protocol.packet.PacketKick({
            target : rest[0],
            msg    : rest.slice(1).join(" ")
        }));

    },

    describe : function()
    {
        apollo.client.util.ui.addConsoleMessage("/kick user [reason] - Kicks user for [reason]");
    }
});
