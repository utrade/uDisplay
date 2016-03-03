/*
 * static/uDisplay/js/collections/accounts_data.js
 * Created by Mayank Jain
 */

var app = app || {}

app.AccountsData = Backbone.Collection.extend({
    model: app.Accounts,

    localStorage: new Backbone.LocalStorage("accounts-backbone"),

});
