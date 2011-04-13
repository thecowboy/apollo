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

dojo.require("dojo.parser");

dojo.require("dijit.Dialog");

dojo.require("dijit.form.Form");
dojo.require("dijit.form.Button");
dojo.require("dijit.form.TextBox");

dojo.require("dijit.ProgressBar");
dojo.require("dijit.TitlePane");

dojo.require("dijit.layout.BorderContainer");
dojo.require("dijit.layout.ContentPane");

dojo.require("dijit.TooltipDialog");

dojo.require("dijit.Menu");
dojo.require("dijit.MenuBar");
dojo.require("dijit.PopupMenuBarItem");
dojo.require("dijit.MenuItem");
dojo.require("dijit.MenuSeparator");

dojo.baseUrl = "static/lib/dojo/"; // dojo WOULD be here

dojo.registerModulePath("apollo.client.dylib", "../../../dylib"); // for dynamic libraries

dojo.require("apollo.client.Core");
dojo.require("apollo.client.util.ui");

var core;

dojo.addOnLoad(function()
{
    dojo.parser.parse();
    dojo.fadeOut({
        node: "loadingOverlay",
        onEnd : function()
        {
            dojo.destroy(dojo.byId("loadingOverlay"));
        }
    }).play();
    (core = new apollo.client.Core()).go();
});

