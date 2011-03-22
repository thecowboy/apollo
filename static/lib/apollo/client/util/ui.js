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

dojo.provide("apollo.client.util.ui");

apollo.client.util.ui.addChatMessage = function(origin, message)
{
    var row = dojo.create("tr", null, "chatLog");
    var col = dojo.create("td", null, row);

    var chatOrigin = dojo.create("span");
    dojo.addClass(chatOrigin, "chatOrigin");
    chatOrigin.innerHTML = origin + ": ";

    var chatMessage = dojo.create("span");
    dojo.addClass(chatMessage, "chatMessage");
    // let's do the angle bracket dance!
    chatMessage.innerHTML = apollo.client.util.ui.linkify(message.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"));

    dojo.place(chatOrigin, col);
    dojo.place(chatMessage, col);

    // do scroll
    var chatPane = dojo.byId("chatPane");
    chatPane.scrollTop = chatPane.scrollHeight;
}

apollo.client.util.ui.addConsoleMessage = function(message)
{
    var row = dojo.create("tr", null, "chatLog");

    var chatConsole = dojo.create("td");
    dojo.addClass(chatConsole, "chatConsole");
    chatConsole.innerHTML = apollo.client.util.ui.linkify(message);

    dojo.place(chatConsole, row);

    // do scroll
    var chatPane = dojo.byId("chatPane");
    chatPane.scrollTop = chatPane.scrollHeight;
}

apollo.client.util.ui.setUserData = function(name, level, profession, hp, ap, xp)
{
    var namefield = dojo.byId("infoUserName");
    var levelfield = dojo.byId("infoUserLevel");
    var proffield = dojo.byId("infoUserProfession");

    var hpfield = dijit.byId("infoUserHP");
    var apfield = dijit.byId("infoUserAP");
    var xpfield = dijit.byId("infoUserXP");

    namefield.innerHTML = name;
    levelfield.innerHTML = level;
    proffield.innerHTML = profession;

    hpfield.update({ progress : hp.now, maximum : hp.max });
    hpfield.label.innerHTML = hp.now + " / " + hp.max;

    apfield.update({ progress : ap.now, maximum : ap.max });
    apfield.label.innerHTML = ap.now + " / " + ap.max;

    xpfield.update({ progress : xp.now, maximum : xp.max });
}

apollo.client.util.ui.setInfoData = function(location, terrain, things)
{
    var realmfield = dojo.byId("infoThisTileRealm");
    var xfield = dojo.byId("infoThisTileXCoordinate");
    var yfield = dojo.byId("infoThisTileYCoordinate");

    var tile = dojo.byId("infoThisTileImg");
    var things = dojo.byId("infoThisTileThings");

    realmfield.innerHTML = location.realm;
    xfield.innerHTML = location.x;
    yfield.innerHTML = location.y;

    tile.src = "static/tiles/" + terrain.img + ".png";
    tile.alt = terrain.name;
    tile.title = terrain.name;

    if(things.length == 0)
    {
    }
}

var linkExpr = /(\b(https?|ftp):\/\/[\-A-Z0-9+&@#\/%?=~_|!:,.;]*[\-A-Z0-9+&@#\/%=~_|])/ig;

apollo.client.util.ui.linkify = function(text)
{
    return text.replace(linkExpr, "<a href=\"$1\">$1</a>");
}

