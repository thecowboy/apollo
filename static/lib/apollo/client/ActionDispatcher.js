/*
 * Copyright (C) 2011 by Tony Young
 *                       Ryan Lewis
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
dojo.require("apollo.client.util.ui");

// packets
dojo.require("apollo.client.protocol.packet.PacketLogin");
dojo.require("apollo.client.protocol.packet.PacketLogout");
dojo.require("apollo.client.protocol.packet.PacketChat");

dojo.require("apollo.client.command.HelpCommand");
dojo.require("apollo.client.command.KickCommand");
dojo.require("apollo.client.command.LogoutCommand");
dojo.require("apollo.client.command.WhisperCommand");
dojo.require("apollo.client.command.OnlineCommand");
dojo.require("apollo.client.command.TeleportCommand");
dojo.require("apollo.client.command.WhoisCommand");

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
                    apollo.client.util.sha256.sha256(
                        username.toLowerCase() + ":" + password
                    ) +
                    this.transport.token
                )
            ),
            nonce       : nonce
        }));
    },

    logout : function()
    {
        this.transport.sendAction(new apollo.client.protocol.packet.PacketLogout());
    },

    commandMappings : {
        help    : apollo.client.command.HelpCommand,
        logout  : apollo.client.command.LogoutCommand,
        camp    : apollo.client.command.LogoutCommand,
        kick    : apollo.client.command.KickCommand,
        w       : apollo.client.command.WhisperCommand,
        whisper : apollo.client.command.WhisperCommand,
        tell    : apollo.client.command.WhisperCommand,
        msg     : apollo.client.command.WhisperCommand,
        list    : apollo.client.command.OnlineCommand,
        online  : apollo.client.command.OnlineCommand,
        teleport: apollo.client.command.TeleportCommand,
        tp      : apollo.client.command.TeleportCommand,
        whois   : apollo.client.command.WhoisCommand
    },

    chat : function(msg)
    {
        if(msg[0] == "/")
        {
            if(msg[1] != "/")
            {
                var parts = msg.split(" ");
                var rest = parts.slice(1);
                var command = this.commandMappings[parts[0].substring(1).toLowerCase()];

                if(command === undefined)
                {
                    apollo.client.util.ui.addConsoleMessage("Command not recognized.");
                    return;
                }

                command.prototype.execute.apply(new command, [ this.transport ].concat(rest));
                return;
            }
            msg = msg.substring(1);
        }
        this.transport.sendAction(new apollo.client.protocol.packet.PacketChat({ msg: msg }));
    }
});
