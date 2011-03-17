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

dojo.provide("apollo.client.UIRoot");

dojo.require("apollo.client.Component");
dojo.require("apollo.client.util.EvaluationContext");

dojo.require("dijit._Widget");

dojo.require("dojo.parser");

dojo.declare("apollo.client.UIRoot", apollo.client.Component, {
    constructor : function(core)
    {
        dojo.addClass(dojo.body(), "claro");
        this.uiElements = {};
    },

    hideAll : function()
    {
        for(var key in this.uiElements)
        {
            this.uiElements[key].hide();
        }
    },

    showAll : function()
    {
        for(var key in this.uiElements)
        {
            this.uiElements[key].show();
        }
    },

    clear : function()
    {
        for(var key in this.uiElements)
        {
            this.remove(key);
        }
    },

    add : function(id, type)
    {
        var that = this;

        var res = "static/ui/" + type;

        var widget = new dijit._Widget();

        this.uiElements[id] = widget;

        var tempNode = dojo.create("div", null);

        var loadContent = function(callback)
        {
            dojo.xhrGet({
                url         : res + ".html",
                handleAs    : "text",
                load        : function(data)
                {
                    tempNode.innerHTML = data;
                    dojo.safeMixin(widget, dojo.parser.parse(tempNode)[0]);
                    widget.apollo = {
                        uiroot : that,
                        core   : that.core
                    };
                    callback();
                }
            });
        };

        dojo.xhrGet({
            url             : res + ".js",
            handleAs        : "text",
            load            : function(data)
            {
                var context = new apollo.client.util.EvaluationContext();
                context.eval(data);

                if(context.preLoad) context.preLoad(widget);

                dojo.ready(function()
                {
                    loadContent(function()
                    {
                        if(context.postLoad) context.postLoad(widget);
                        if(!that.uiElements[id])
                        {
                            widget.destroy();
                            if(dijit._dialogStack.length) dijit._underlay.show();
                        }
                    });
                });
            },
            error           : loadContent
        });

        return widget;
    },

    remove : function(id)
    {
        if(!this.uiElements[id]) return;

        this.uiElements[id].destroy();
        delete this.uiElements[id];
    }
});
