(function() {
    'use strict';

    var roommate = angular.module('roommate', ['ui.router'])
        .config(function($interpolateProvider, $stateProvider, $urlRouterProvider) {
            $interpolateProvider.startSymbol('[[');
            $interpolateProvider.endSymbol(']]');

            $urlRouterProvider.otherwise('/dashboard');
            $stateProvider.state({
                name: 'dashboard',
                url: '/dashboard',
                templateUrl: '/static/roommate/views/dashboard/dash-board-view.html',
                controller: 'dashboardController'
            }).state({
                name: 'charts',
                url: '/charts',
                templateUrl: '/static/roommate/views/charts/charts.view.html',
                controller: 'chartsController'
            }).state({
                name: 'mail',
                url: '/main',
                templateUrl: '/static/roommate/views/mail/mail.view.html',
                controller: 'mailController'
            })

        }).controller('loginController', function($scope, $http) {
            $scope.title = "Room Mate";
            $scope.login = function(data) {
                console.log(data);
                $('#login-spinner-login').removeClass().addClass('fa fa-spinner fa-spin');
            }

            $scope.register = function(data) {
                console.log(data);
                $('#login-spinner-egister').removeClass().addClass('fa fa-spinner fa-spin');
            }

        }).controller('dashboardController', function($scope, $rootScope, $http) {

            $scope.sample = function() {
                console.log('Welcome from from dashboard controller');
            }
        }).controller('chartsController', function($scope, $rootScope, $http) {
            $scope.sample = function() {
                console.log('charts Controller called')
            }
        }).controller('mailController', function($scope, $rootScope, $http) {
            $scope.sample = function() {
                console.log('mail Controller called')
            }
        });
})();