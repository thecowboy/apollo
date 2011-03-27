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
dojo.require("dijit.MenuItem");

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
