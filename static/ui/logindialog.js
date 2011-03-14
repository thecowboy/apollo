this.preLoad = function(dialog)
{
    dojo.require("dijit.form.Form");
    dojo.require("dijit.form.Button");
    dojo.require("dijit.form.TextBox");

    dialog.attr("title", "Login");
    dialog.closeButtonNode.style.display = "none";
};

this.postLoad = function(dialog)
{
};
