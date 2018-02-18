(function() {
    'use strict';

    var roommate = angular.module('roommate', [])
        .config(function($interpolateProvider) {
            $interpolateProvider.startSymbol('[[');
            $interpolateProvider.endSymbol(']]');
        }).controller('loginController', function($scope, $http) {

            $scope.title = "Room Mate";
            $scope.login = function(data) {
                console.log(data);
                $('#login-spinner').removeClass().addClass('fa fa-spinner fa-spin');
            }

        })
})();