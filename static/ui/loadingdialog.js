this.preLoad = function(dialog)
{
    dialog.attr("title", "Loading");
    dialog.closeButtonNode.style.display = "none";
    dialog._onKey = function() { };
};
