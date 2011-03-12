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

dojo.provide("apollo.client.ui.elements.LoginDialog");

dojo.require("dijit.Dialog");
dojo.require("dijit.form.Form");
dojo.require("dijit.form.Button");
dojo.require("dijit.form.TextBox");

dojo.require("apollo.client.ui.elements.Element");

dojo.declare("apollo.client.ui.elements.LoginDialog", apollo.client.ui.elements.Element, {
    constructor : function()
    {
        var that = this;

        this.dialog = new dijit.Dialog({ title : "Login" });
        this.id = this.dialog.id;

        this.dialog.onHide = function()
        {
            that.destroy();
            return true;
        };

        var loginForm = new dijit.form.Form();
        loginForm.onSubmit = function()
        {
            that.hide();
            return false;
        };

        var loginBody = dojo.create("table", null, loginForm.domNode);

        var usernameRow = dojo.create("tr", null, loginBody);

        var usernameLabelCol = dojo.create("td", null, usernameRow);
        var usernameLabel = dojo.create("label", {
            "for"       : "login_username",
            "innerHTML" : "Username"
        }, usernameLabelCol);

        var usernameFieldCol = dojo.create("td", null, usernameRow);
        var usernameField = new dijit.form.TextBox(null, "login_username");
        dojo.place(usernameField.domNode, usernameFieldCol, "last");

        var passwordRow = dojo.create("tr", null, loginBody);

        var passwordLabelCol = dojo.create("td", null, passwordRow);
        var passwordLabel = dojo.create("label", {
            "for"       : "login_password",
            "innerHTML" : "Password"
        }, passwordLabelCol);

        var passwordFieldCol = dojo.create("td", null, passwordRow);
        var passwordField = new dijit.form.TextBox({ type : "password" }, "login_password");
        dojo.place(passwordField.domNode, passwordFieldCol, "last");

        var buttonRow = dojo.create("tr", {
            colspan     : 2
        }, loginBody);
        var loginButton = new dijit.form.Button({
            "label"     : "Login",
            "type"      : "submit"
        });
        dojo.place(loginButton.domNode, buttonRow, "last");

        this.dialog.attr("content", loginForm);
        this.dialog.closeButtonNode.style.display = "none";
    },

    show : function()
    {
        this.dialog.show.apply(this.dialog, arguments);
    },

    hide : function()
    {
        this.dialog.hide.apply(this.dialog, arguments);
    },

    destroy : function()
    {
        this.dialog.destroy();
        this.inherited(arguments);
    },
});
