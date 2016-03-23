/*
 * static/js/collections/accounts_data.js
 */

var app = app || {}

app.AccountsData = Backbone.Collection.extend({
    model: app.Accounts,

    localStorage: new Backbone.LocalStorage("accounts-backbone"),

});
