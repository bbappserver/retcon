(function(angular) {
  'use strict';

const routes=
[

];

const controllers=
[
  'BookController','ChapterController',
  'PersonController','SeriesController'
];

const mainModule=angular.module('ngRouteExample', ['ngRoute']);
const MAIN_STATIC_FILES_URL= STATIC_FILES_URL_ROOT+'main/';

 mainModule.controller('MainController', function($scope, $route, $routeParams, $location) {
     $scope.$route = $route;
     $scope.$location = $location;
     $scope.$routeParams = $routeParams;
 });

// for(let c in controllers)
// {
//   mainModule.controller(c, function($scope, $routeParams) {
//      $scope.name = c;
//      $scope.params = $routeParams;
//  });
// }

mainModule.controller('BookController', function($scope, $routeParams) {
  $scope.name = 'BookController';
  $scope.appName='main';
  $scope.params = $routeParams;
  $scope.staticFileRoot=STATIC_FILES_URL_ROOT+$scope.appName;
});

mainModule.controller('ChapterController', function($scope, $routeParams) {
  $scope.name = 'ChapterController';
  $scope.params = $routeParams;
});

mainModule.config(function($routeProvider, $locationProvider) {
  $routeProvider
   .when('/Book/:bookId', {
    templateUrl: MAIN_STATIC_FILES_URL+'book.html',
    controller: 'BookController',
    resolve: {
      // I will cause a 1 second delay
      delay: function($q, $timeout) {
        var delay = $q.defer();
        $timeout(delay.resolve, 1000);
        return delay.promise;
      }
    }
  })
  .when('/Book/:bookId/ch/:chapterId', {
    templateUrl: MAIN_STATIC_FILES_URL+'chapter.html',
    controller: 'ChapterController'
  })
  .when('/Person/:personId/ch/:chapterId', {
    templateUrl: MAIN_STATIC_FILES_URL+'chapter.html',
    controller: 'ChapterController'
  });

  // configure html5 to get links working on jsfiddle
  $locationProvider.html5Mode(true);
});

})(window.angular);

/*
Copyright 2020 Google Inc. All Rights Reserved.
Use of this source code is governed by an MIT-style license that
can be found in the LICENSE file at http://angular.io/license
*/