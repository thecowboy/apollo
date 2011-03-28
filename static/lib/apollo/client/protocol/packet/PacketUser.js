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

dojo.provide("apollo.client.protocol.packet.PacketUser");

dojo.require("apollo.client.protocol.packet.Packet");

dojo.require("apollo.client.util.ui");

dojo.declare("apollo.client.protocol.packet.PacketUser", apollo.client.protocol.packet.Packet, {
    name    : "user",

    dispatch : function(transport, core)
    {
        if(this.target === undefined)
        {
            apollo.client.util.ui.setUserData(
                this.name,
                this.level,
                this.profession,
                this.hp,
                this.ap,
                this.xp
            )
        } else {
            apollo.client.util.ui.addConsoleMessage(
                    "About " + this.name + ", the level " + this.level + " " + this.profession + ":\n" +
                    "HP: " + this.hp.now + "/" + this.hp.max + "\n" +
                    "AP: " + this.ap.now + "/" + this.ap.max + "\n" +
                    "XP: " + this.xp.now + "/" + this.xp.max + "\n" +
                    "Location: (" + this.location.x + ", " + this.location.y + ")"
            );
        }
    }
});
