/*
 * Accounts Extended JS
 * static/js/accounts_extended.js
 *
 */


// Initialising Backbone app
var app = app || {};
// Initialising Backbone Collection
var data_collection;

/**
 * Update recieved data to backbone
 * @param Socket Data as result
 */
function update_data(result) {
    if (result && result.hasOwnProperty('updaterisk')) {
        var data = result['updaterisk']['riskdata']
        data['accountid'] = result['updaterisk']['accountid']
    }
    if (result && result.hasOwnProperty('updateaccount')) {
        var data = result['updateaccount']['accountdata']
    }

    if (data && data['error'] == null) {

        // Merge updated data
        data_collection.add([data],{merge: true});

        // Removes Loader
        if($(".spinner").length > 0) {
            document.getElementsByClassName('.spinner')[0];
            $(".spinner").remove();
        }
    }
    else {

        // TODO: Check error in result
        console.log(result['Error']);
    }
}

/**
 * Establishes connection with Tornado socket to
 * receive market data and notifications from CCL through SockJS object.
 */
function ConnectSocket() {
    var domain_name = location.hostname;

    // Change socket connection from http to https
    var socket_link = 'http://' + (domain_name.split(':')[0]) + ':'+ port + socket_path;
    //var socket_link = 'https://' + (domain_name.split(':')[0]) + socket_path;

    conn = new SockJS(socket_link, {debug:true});
    conn.onopen = function() {
        if (conn == null) {
            ConnectSocket();
            return false;
        }
        conn.send('add;' + username + ';' + token);
        console.log('socket opened');
    };

    conn.onmessage = function(e) {
        if (e.data != 'add') {
            if(e.data == 'Logout') {
                // If logout from backend
                window.location.href = "http://" + location.host;
                //window.location.href = "https://" + location.host;
            }
            else {
                update_data(e.data);
                console.log("Message: ", e.data);
            }
        }
    };

    conn.onclose = function(e) {
        conn.send('del;' + username);
        console.log("socket closed");
        setTimeout(function(){ ConnectSocket(); },5000);
    };
}

// Initialising Backbone model from Django Initial Data
$(document).ready(function() {

    // Backbone Collection
    data_collection = new app.AccountsData( data );
    //Initialize Backbone View
    InitialView = new app.AccountsView( data, data_collection );

    // Data not available than insert Loading
    if (data.length && data[0].hasOwnProperty('error')) {
        var newElement = '<div class="spinner"><div class="loader"></div></div>'
         $(".accounts_table").append(newElement);
    }

    // release from memory
    data = null;

    ConnectSocket();

    /**
     * function for making search case insensitive
     */
    jQuery.expr[':'].Contains = function(a,i,m){
        return jQuery(a).text().toUpperCase().indexOf(m[3].toUpperCase())>=0; // ==0 for exact match
    };

    /**
     * function for search
     */
    $('#search_name').keyup(function() {
        search_name = $(this).val();
        $('#names tr').children().show();
        if (jQuery.trim(search_name) != '') {
            $("#names #account_name:not(:Contains('"+ search_name +"'))").parent().children().hide();
            $("#names #account_name:not(:Contains('"+ search_name +"'))").parent().next().children().hide();
        }
        else {
            $('#names tr').children().show();
        }
    });

    /**
     * function for search inside Account Picker
     */
    $('#accounts_search').keyup(function() {
        search_name = $(this).val();
        $('.accounts_picker_body .checkbox').show();
        if (jQuery.trim(search_name) != '') {
            $(".accounts_picker_body .checkbox label:not(:Contains('"+ search_name +"'))").parent().hide();
        }
        else {
            $('.accounts_picker_body .checkbox').show();
        }
    });

    /**
     * Stops submit on enter in search form
     */
    $('#search_name').keydown(function(event){
        if(event.keyCode == 13) {
            event.preventDefault();
            return false;
        }
    });

    /**
     * Saving Accounts selection on server
     */
    $("#selectedAccounts").on('click', function () {
        if ($(".checkbox input:checkbox:checked").length > 0) {
            var newElement = '<div class="spinner"><div class="loader"></div></div>'
            $(".accounts_picker_body").prepend(newElement);

            var valuesArray = [];
            $("input:checked").each(function() {
                valuesArray.push($(this).val());
            });
            var params = {};
            params.accounts = valuesArray;
            $.getJSON("/save_accounts/", $.param(params, true), function(result){
                console.log("Accounts saved: ",result);
                window.location.href = "http://" + location.host;
            });
        } else {
            alert("Please select atleast one account!!");
        }
    });

    /**
     * Bulk Select/UnSelect Accounts in Account Picker
     */
    $(".bulk_select").on('click', function () {
        if($(".checkbox input").length == $(".checkbox input:checked").length) {
            if($(".bulk_select").html() != "Select All") {
                $(".checkbox input").prop('checked', false);
                $(".bulk_select").html("Select All");
            }
            else {
                $(".checkbox input").prop('checked', true);
                $(".bulk_select").html("Unselect All")
            }
        }
        else {
            $(".checkbox input").prop('checked', true);
            $(".bulk_select").html("Unselect All")
        }
    });

    /**
     * Check the selected accounts on account picker modal show
     */
    $('#selectAccounts').on('show.bs.modal', function (e) {
        $(".checkbox input").prop('checked', false);
        selected_accounts.forEach(function(itemInArray) {
            $(".account_picker_"+itemInArray+" input").prop('checked', true);
        });
        $(".bulk_select").html("Select All");
    });

    /**
     * Initialize tooltips
     */
    $(function () {
        $('[data-toggle="tooltip"]').tooltip()
    });

    /**
     * Initialize tooltip for Accounts Picker
     * As it already have data-toggle for modal
     */
    $(function() {
        $('[rel="tooltip"]').tooltip();
    });
});
