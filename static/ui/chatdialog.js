this.preLoad = function(dialog)
{
    dialog.attr("title", "Chat");
    dialog.titleBar.style.display = "none";
    dialog.containerNode.style.background = "none";
    dialog.containerNode.style.border = "none";
    dialog.domNode.style.border = "none";
    dialog.domNode.style.boxShadow = "none";
    dialog._onKey = function() { };
};

this.postLoad = function(dialog)
{
};
