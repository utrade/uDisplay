/*
 * static/js/models/accounts.js
 */

var app = app || {};

app.Accounts = Backbone.Model.extend({
    idAttribute: 'accountid',
    defaults: {
        "accountid" : 0,
        "accountname" : "-",
        "netLiquidity" : "0.0",
        "netProfitLoss" : "0.0",
        "netMargin" : "0.0",
        "netBalance" : "0.0",
        "netEquity" : "0.0",
    },
});
