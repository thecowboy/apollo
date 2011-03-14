this.preLoad = function(dialog)
{
    dialog.attr("title", "Error");
    dialog.closeButtonNode.style.display = "none";
};

this.postLoad = function(dialog)
{
    dijit.getEnclosingWidget(dojo.query(".errorPane", dialog.domNode)[0]).attr("content", dialog.message);
};
