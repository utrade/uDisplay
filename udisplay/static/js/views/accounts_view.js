/*
 * static/js/views/accounts_view.js
 */

/**
 * Function for Formatting the numbers
 * :param Number as n
 * :param Number Type as type (int/float)
 */
format = function (n, type) {
    if(type === 'float'){
        return parseFloat(n).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,");
    }
    if(type === 'int'){
        return parseInt(n).toFixed().replace(/(\d)(?=(\d{3})+\.)/g, "$1,");
    }
}

/**
 * Initialize backbone app
 */
var app = app || {};

/**
 * Accounts rows View
 * :param Backbone Model as this.model
 */
app.AccountView = Backbone.View.extend({
    tagName: "tr",
    className: 'account_row',
    template: _.template($('#account_row').html()),

    render: function() {
        this.$el.html(this.template(this.model.toJSON()));
        return this;
    },

});

app.AccountsView = Backbone.View.extend({
    el: '.accounts_tbody',
    tagName: 'table',
    className: 'table table-condensed table-bordered table-hover accounts_tbody',
    template: _.template( $('#accounts_page').html() ),

    // Make it easier to change later
    //sortUpIcon: 'caret-up',
    //sortDnIcon: 'caret',
    sortUpIcon: '',
    sortDnIcon: '',

    initialize: function( initialData, data_collection ) {
        this.collection = data_collection
        this.totalAccounts = 0; // Saving Number of Total Accounts
        this.render();

        this.listenTo(this.collection, 'add', this.addOne);
        this.listenTo(this.collection, 'change', this.updateOne);
    },

    // render data by each row
    render: function() {

        // Reset totalAccounts
        this.totalAccounts = 0;

        this.$el.html(this.template());
        $('.accounts_picker_body').html('');
        this.collection.each(function( account ) {
            if(account.attributes.error){
                // Empty or default model
                console.log("Error--->>" + account.attributes.error);
                this.collection.remove(account);
            }
            else{
                this.addOne(account);
            }
        }, this );

        // Setup the sort indicators
        $('.accounts_head_row th div')
            .append($('<span>'))
            .closest('thead')
            .find('span')
            .addClass('icon-none');
        if(this.collection.sortDirection == 1) {
            $('.accounts_head_row th div')
            .end()
            .find('[column="'+this.collection.sortAttribute+'"] span')
            .removeClass('icon-none').addClass(this.sortUpIcon);
        }
        else {
            $('.accounts_head_row th div')
            .end()
            .find('[column="'+this.collection.sortAttribute+'"] span')
            .removeClass('icon-none').addClass(this.sortDnIcon);
        }

        /**
         * Initialize tooltips
         */
        $(function () {
            $('[data-toggle="tooltip"]').tooltip('destroy');
            $('[data-toggle="tooltip"]').tooltip();
        });
    },

    // append new row if something added
    addOne: function( item ) {

        this.totalAccounts += 1;

        var account_view = new app.AccountView({ model: item });
        this.$el.append(account_view.render().el);
    },

    // update already added row
    updateOne: function( item ) {

        // Checking if item is alredy visible to user or not
        if($(".accountid_"+item.attributes['accountid']).is(":visible")) {
            var collapse_flag = false;
            var account_view = new app.AccountView({ model: item });
            $(".accountid_"+item.attributes['accountid']).parent().replaceWith(account_view.render().el);
        }
    },
});
