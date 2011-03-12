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

dojo.provide("apollo.client.ui.UIRoot");

dojo.require("apollo.client.Component");

dojo.declare("apollo.client.ui.UIRoot", apollo.client.Component, {
    constructor : function(core)
    {
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
            this.uiElements[key].destroy();
        }
        this.uiElements = {};
    },

    add : function(type)
    {
        var element = new type(this, this.core);
        this.uiElements[element.id] = element;
        return element;
    },

    remove : function(id)
    {
        this.uiElements[id].destroy();
        delete this.uiElements[id];
    }
});
