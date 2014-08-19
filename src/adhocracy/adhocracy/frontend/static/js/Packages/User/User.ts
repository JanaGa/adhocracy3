import AdhHttp = require("../Http/Http");
import AdhConfig = require("../Config/Config");

var pkgLocation = "/User";

export interface IUserBasic {
    name? : string;
    email? : string;
    tzname? : string;
}


interface IScopeLogin {
    user : User;
    credentials : {
        nameOrEmail : string;
        password : string;
    };
    errors : string[];

    resetCredentials : () => void;
    logIn : () => ng.IPromise<void>;
}


interface IScopeRegister {
    input : {
        username : string;
        email : string;
        password : string;
        passwordRepeat : string;
    };
    errors : string[];

    register : () => ng.IPromise<void>;
}


export interface IRegisterResponse {}


var bindServerErrors = (
    $scope : {errors : string[]},
    errors : AdhHttp.IBackendErrorItem[]
) => {
    $scope.errors = [];
    if (!errors.length) {
        $scope.errors.push("Unknown error from server (no details provided)");
    } else {
        errors.forEach((e) => {
            $scope.errors.push(e.description);
        });
    }
};


export class User {
    public loggedIn : boolean = false;
    public data : IUserBasic;
    private token : string;

    constructor(
        private adhHttp : AdhHttp.Service<any>,
        private $q : ng.IQService,
        private $http : ng.IHttpService,
        private $window : Window,
        private Modernizr
    ) {
        var _self : User = this;

        if (_self.Modernizr.localstorage) {
            if (_self.$window.localStorage.getItem("user-token") !== null &&
                    _self.$window.localStorage.getItem("user-path") !== null) {
                _self.enableToken(
                    _self.$window.localStorage.getItem("user-token"),
                    _self.$window.localStorage.getItem("user-path")
                );
            }
        }
    }

    private enableToken(token : string, userPath : string) : ng.IPromise<void> {
        var _self : User = this;

        _self.token = token;
        _self.$http.defaults.headers.common["X-User-Token"] = token;
        _self.$http.defaults.headers.common["X-User-Path"] = userPath;
        _self.loggedIn = true;

        return _self.adhHttp.get(userPath)
            .then((resource) => {
                _self.data = resource.data["adhocracy.sheets.user.IUserBasic"];
                return resource;  // FIXME this is only here because of a bug in DefinitelyTyped
            }, (reason) => {
                // The user resource that was returned by the server could not be accessed.
                // This may happen e.g. with a network disconnect
                _self.deleteToken();
                return _self.$q.reject("failed to fetch user resource");
            });
    }

    private storeAndEnableToken(token : string, userPath : string) : ng.IPromise<void> {
        var _self : User = this;

        if (_self.Modernizr.localstorage) {
            _self.$window.localStorage.setItem("user-token", token);
            _self.$window.localStorage.setItem("user-path", userPath);
        } else {
            console.log("session could not be persisted");
        }

        return _self.enableToken(token, userPath);
    }

    private deleteToken() : void {
        var _self : User = this;

        if (_self.Modernizr.localstorage) {
            _self.$window.localStorage.removeItem("user-token");
            _self.$window.localStorage.removeItem("user-path");
        }
        delete _self.$http.defaults.headers.common["X-User-Token"];
        delete _self.$http.defaults.headers.common["X-User-Path"];
        _self.token = undefined;
        _self.data = undefined;
        _self.loggedIn = false;
    }

    public logIn(nameOrEmail : string, password : string) : ng.IPromise<void> {
        var _self : User = this;
        var promise;

        // NOTE: the post requests here do not contain resources in
        // the body, so adhHttp must not be used (because it
        // implicitly does importContent / exportContent which expect
        // Types.Content)!

        if (nameOrEmail.indexOf("@") === -1) {
            promise = _self.$http.post("/login_username", {
                name: nameOrEmail,
                password: password
            });
        } else {
            promise = _self.$http.post("/login_email", {
                email: nameOrEmail,
                password: password
            });
        }

        var success = (response) => {
            // FIXME use websockets for updates
            return _self.storeAndEnableToken(response.data.user_token, response.data.user_path);
        };

        return promise
            .then(success, AdhHttp.logBackendError);
    }

    public logOut() : void {
        var _self : User = this;

        // The server does not have a logout yet.
        _self.deleteToken();
    }

    public register(username : string, email : string, password : string, passwordRepeat : string) : ng.IPromise<IRegisterResponse> {
        var _self : User = this;

        return _self.adhHttp.post("/principals/users/", {
            "content_type": "adhocracy.resources.principal.IUser",
            "data": {
                "adhocracy.sheets.user.IUserBasic": {
                    "name": username,
                    "email": email
                },
                "adhocracy.sheets.user.IPasswordAuthentication": {
                    "password": password
                }
            }
        });
    }

    public can(permission : string) {
        var _self : User = this;

        // FIXME this is only a dummy implementation
        return _self.loggedIn;
    }
}


export var loginDirective = (adhConfig : AdhConfig.Type) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Login.html",
        scope: {},
        controller: ["adhUser", "$scope", (adhUser : User, $scope : IScopeLogin) : void => {
            $scope.errors = [];

            $scope.credentials = {
                nameOrEmail: "",
                password: ""
            };

            $scope.resetCredentials = () => {
                $scope.credentials.nameOrEmail = "";
                $scope.credentials.password = "";
            };

            $scope.logIn = () => {
                var promise = adhUser.logIn(
                    $scope.credentials.nameOrEmail,
                    $scope.credentials.password
                ).then(() => {
                    $scope.errors = [];
                }, (errors) => {
                    bindServerErrors($scope, errors);
                });
                $scope.resetCredentials();
                return promise;
            };
        }]
    };
};


export var registerDirective = (adhConfig : AdhConfig.Type, $location : ng.ILocationService) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Register.html",
        scope: {},
        controller: ["adhUser", "$scope", (adhUser : User, $scope : IScopeRegister) => {
            $scope.input = {
                username: "",
                email: "",
                password: "",
                passwordRepeat: ""
            };

            $scope.errors = [];

            $scope.register = () : ng.IPromise<void> => {
                return adhUser.register($scope.input.username, $scope.input.email, $scope.input.password, $scope.input.passwordRepeat)
                    .then((response) => {
                        $scope.errors = [];
                        return adhUser.logIn($scope.input.username, $scope.input.password).then(
                            () => { $location.path("/frontend_static/root.html"); },
                            (errors) => bindServerErrors($scope, errors)
                        );
                    }, (errors) => bindServerErrors($scope, errors));
            };
        }]
    };
};


export var indicatorDirective = (adhConfig : AdhConfig.Type) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Indicator.html",
        scope: {},
        controller: ["adhUser", "$scope", (adhUser : User, $scope) => {
            $scope.user = adhUser;
            $scope.pkgUrl = adhConfig.pkg_path + pkgLocation;

            $scope.logOut = () => {
                adhUser.logOut();
            };
        }]
    };
};


export var metaDirective = (adhConfig : AdhConfig.Type) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Meta.html",
        scope: {
            path: "@"
        },
        controller: ["adhHttp", "$scope", (adhHttp : AdhHttp.Service<any>, $scope) => {
            if ($scope.path) {
                adhHttp.resolve($scope.path)
                    .then((res) => {
                        $scope.userBasic = res.data["adhocracy.sheets.user.IUserBasic"];
                        $scope.isAnonymous = false;
                    });
            } else {
                $scope.userBasic = {
                    name: "anonymous",
                };
                $scope.isAnonymous = true;
            }
        }]
    };
};
