this.preLoad = function(dialog)
{
    dialog.attr("title", "Error");
    dialog.closeButtonNode.style.display = "none";
    dialog._onKey = function(evt) { if(evt.charOrCode != dojo.keys.ESCAPE) return dijit.form.Dialog.prototype._onKey(evt); };
};

this.postLoad = function(dialog)
{
    dijit.getEnclosingWidget(dojo.query(".errorPane", dialog.domNode)[0]).attr("content", dialog.message);
};
