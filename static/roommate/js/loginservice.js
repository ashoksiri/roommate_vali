(function() {
    'use strict';

    angular
        .module('Module')
        .service('Service', Service);

    Service.$inject = ['dependency1'];

    function Service(dependency1) {
        this.exposedFn = exposedFn;

        ////////////////

        function exposedFn() {}
    }
})();