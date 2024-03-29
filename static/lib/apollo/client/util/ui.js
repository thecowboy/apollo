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

dojo.require("dijit.MenuItem");

apollo.client.util.ui.sanitize = function(data)
{
    // let's do the angle bracket dance!
    return data
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
};

apollo.client.util.ui.addChatMessage = function(origin, message)
{
    var row = dojo.create("tr", null, "chatLog");
    var col = dojo.create("td", null, row);

    var chatOrigin = dojo.create("span");
    dojo.addClass(chatOrigin, "chatOrigin");
    chatOrigin.innerHTML = origin + ": ";

    var chatMessage = dojo.create("span");
    dojo.addClass(chatMessage, "chatMessage");
    chatMessage.innerHTML = apollo.client.util.ui.linkify(apollo.client.util.ui.sanitize(message));

    dojo.place(chatOrigin, col);
    dojo.place(chatMessage, col);

    // do scroll
    var chatPane = dojo.byId("chatPane");
    chatPane.scrollTop = chatPane.scrollHeight;
};

apollo.client.util.ui.addConsoleMessage = function(message)
{
    var lines = message.split("\n");

    for(var i = 0; i < lines.length; ++i)
    {
        var row = dojo.create("tr", null, "chatLog");

        var chatConsole = dojo.create("td");
        dojo.addClass(chatConsole, "chatConsole");
        chatConsole.innerHTML = apollo.client.util.ui.linkify(apollo.client.util.ui.sanitize(lines[i]));

        dojo.place(chatConsole, row);

        // do scroll
        var chatPane = dojo.byId("chatPane");
        chatPane.scrollTop = chatPane.scrollHeight;
    }
};

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
};

apollo.client.util.ui.setInfoData = function(location, terrain, things)
{
    var realmfield = dojo.byId("infoThisTileRealm");
    var xfield = dojo.byId("infoThisTileXCoordinate");
    var yfield = dojo.byId("infoThisTileYCoordinate");

    var tile = dojo.byId("infoThisTileImg");
    var thingsMenu = dijit.byId("infoThisTileThings");
    thingsMenu.destroyDescendants();

    realmfield.innerHTML = location.realm;
    xfield.innerHTML = location.x;
    yfield.innerHTML = location.y;

    tile.src = "static/tiles/" + terrain.img + ".png";
    tile.alt = terrain.name;
    tile.title = terrain.name;

    if(things.length == 0)
    {
        var tumbleweed = new dijit.MenuItem({ "label" : "There is nothing of interest here. -tumbleweed-" });
        tumbleweed.domNode.style.fontStyle = "italic";
        thingsMenu.addChild(tumbleweed);
    } else {
        for(var i = 0; i < things.length; ++i)
        {
            var thing = things[i];

            var thingChild = dojo.create("div");
            thingChild.style.display = "inline";

            var thingName = dojo.create("div");
            thingName.innerHTML = thing.name;
            thingName.style.fontWeight = "bold";
            dojo.place(thingName, thingChild);

            var thingType = dojo.create("div");
            thingType.innerHTML = thing.type;
            dojo.place(thingType, thingChild);

            thingsMenu.addChild(dijit.MenuItem({ "label" : thingChild.innerHTML }));
        }
    }
};

var linkExpr = /(\b(https?|ftp):\/\/[\-A-Z0-9+&@#\/%?=~_|!:,.;]*[\-A-Z0-9+&@#\/%=~_|])/ig;

apollo.client.util.ui.linkify = function(text)
{
    return text.replace(linkExpr, "<a href=\"$1\">$1</a>");
};

apollo.client.util.ui.konami = function(combo, callback)
{
    var state = [];

    return dojo.connect(window, "onkeyup", function(evt)
    {
        state.push(evt.keyCode);
        while(state.length > combo.length)
        {
            state.shift();
        }
        if(state.join(",") == combo.join(","))
        {
            callback();
        }
    });
};
