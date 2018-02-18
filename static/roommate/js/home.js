(function() {
    'use strict';

    document.addEventListener("DOMContentLoaded", function() {
        console.log("Home Page Loaded");

        init();
    });

    function init() {
        var token = get_access_token();
        localStorage.setItem('auth_token', token);
    }


    function get_access_token() {

        return __call_for_response__('get', '/accounts/get_access_token/', {})
    }

    function __call_for_response__(type, url, data, ) {

        $.ajax({
            type: type,
            url: url,
            data: data,
            //dataType: "dataType",
            success: function(response) {
                console.log(response)
                return response;
            },
            error: function(error) {
                console.log(error);
            }
        });
    }



    function loadUsers() {
        $.ajax({
            type: "get",
            url: "/accounts/users/",
            data: "data",
            dataType: "dataType",
            success: function(response) {

            }
        });
    }

})();