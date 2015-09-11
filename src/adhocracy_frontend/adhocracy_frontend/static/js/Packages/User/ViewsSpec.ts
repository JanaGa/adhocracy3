/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>

import * as q from "q";

import * as AdhUserViews from "./Views";


export var register = () => {
    describe("UserViews", () => {
        var adhPermissionsMock;
        beforeEach(() => {
            adhPermissionsMock = {
                bindScope: jasmine.createSpy("adhPermissions.bindScope").and.returnValue("")
            };
        });

        describe("loginDirective", () => {
            var directive;
            var adhConfigMock;
            var adhUserMock;
            var adhTopLevelStateMock;

            beforeEach(() => {
                adhConfigMock = {
                    pkg_path: "mock",
                    root_path: "mock",
                    ws_url: "mock",
                    embedded: true,
                    support_email: "support@adhocracy.com"
                };
                adhUserMock = jasmine.createSpyObj("adhUserMock", ["logIn"]);
                adhUserMock.logIn.and.returnValue(q.when(undefined));
                adhTopLevelStateMock = jasmine.createSpyObj("adhTopLevelStateMock", ["goToCameFrom"]);
                directive = AdhUserViews.loginDirective(
                    adhConfigMock, adhUserMock, adhTopLevelStateMock, adhPermissionsMock, "adhShowError");
            });

            describe("link", () => {
                var scopeMock;

                beforeEach(() => {
                    scopeMock = {
                        loginForm: {
                            $setPristine: () => undefined
                        }
                    };
                    directive.link(scopeMock);
                });

                it("creates an empty credentials object in scope", () => {
                    expect(scopeMock.credentials).toEqual({nameOrEmail: "", password: ""});
                });

                describe("resetCredentials", () => {
                    it("cresets scope.credentials to empty strings", () => {
                        scopeMock.credentials.nameOrEmail = "foo";
                        scopeMock.credentials.password = "bar";

                        scopeMock.resetCredentials();

                        expect(scopeMock.credentials).toEqual({nameOrEmail: "", password: ""});
                    });
                });

                describe("logIn", () => {
                    beforeEach(() => {
                        scopeMock.credentials.nameOrEmail = "foo";
                        scopeMock.credentials.password = "bar";
                    });

                    it("calls adhUser.logIn with scope.nameOrEmail and scope.password", (done) => {
                        scopeMock.logIn().then(() => {
                            expect(adhUserMock.logIn).toHaveBeenCalledWith("foo", "bar");
                            done();
                        });
                    });
                    it("redirects to cameFrom or / if everything goes well", (done) => {
                        scopeMock.logIn().then(() => {
                            expect(adhTopLevelStateMock.goToCameFrom).toHaveBeenCalledWith("/", true);
                            done();
                        });
                    });
                    it("charges $scope.errors if something goes wrong", (done) => {
                        adhUserMock.logIn.and.returnValue(q.reject([{description: "error"}]));
                        scopeMock.logIn().then(() => {
                            expect(scopeMock.errors.length).toBe(1);
                            done();
                        });
                    });
                    it("resets password if something goes wrong", (done) => {
                        adhUserMock.logIn.and.returnValue(q.reject([{description: "error"}]));
                        scopeMock.logIn().then(() => {
                            expect(scopeMock.credentials.password).toBe("");
                            done();
                        });
                    });
                });
            });
        });

        describe("registerDirective", () => {
            var directive;
            var adhConfigMock;
            var adhUserMock;
            var adhTopLevelStateMock;

            beforeEach(() => {
                adhConfigMock = {
                    pkg_path: "mock",
                    root_path: "mock",
                    ws_url: "mock",
                    embedded: true,
                    support_email: "support@adhocracy.com"
                };
                adhUserMock = jasmine.createSpyObj("adhUserMock", ["register", "logIn"]);
                adhUserMock.register.and.returnValue(q.when(undefined));
                adhUserMock.logIn.and.returnValue(q.when(undefined));
                adhTopLevelStateMock = jasmine.createSpyObj("adhTopLevelStateMock", ["goToCameFrom"]);

                directive = AdhUserViews.registerDirective(adhConfigMock, null, adhUserMock, adhTopLevelStateMock, "adhShowError");
            });

            describe("link", () => {
                var scopeMock;

                beforeEach(() => {
                    scopeMock = {
                        $watch: () => undefined,
                        loginForm: {
                            $setPristine: () => undefined
                        }
                    };
                    directive.link(scopeMock);
                });

                it("creates an empty input object in scope", () => {
                    expect(scopeMock.input).toEqual({
                        username: "",
                        email: "",
                        password: "",
                        passwordRepeat: ""
                    });
                });

                describe("register", () => {
                    it("calls adhUser.register with data from scope.input", (done) => {
                        scopeMock.input.username = "username";
                        scopeMock.input.email = "email";
                        scopeMock.input.password = "password";
                        scopeMock.input.passwordRepeat = "passwordRepeat";

                        scopeMock.register().then(() => {
                            expect(adhUserMock.register).toHaveBeenCalledWith("username", "email", "password", "passwordRepeat");
                            done();
                        });
                    });
                    it("does NOT log user in after register ", (done) => {
                        scopeMock.register().then(() => {
                            expect(adhUserMock.logIn).not.toHaveBeenCalled();
                            done();
                        });
                    });
                    xit("redirects came from or / page after register ", (done) => {
                        // FIXME: this condition must now be tested after click on the activation link.
                        scopeMock.register().then(() => {
                            expect(adhTopLevelStateMock.goToCameFrom).toHaveBeenCalledWith("/", true);
                            done();
                        });
                    });
                    it("clear $scope.errors if everything goes well", (done) => {
                        scopeMock.errors = ["error"];
                        scopeMock.register().then(() => {
                            expect(scopeMock.errors.length).toBe(0);
                            done();
                        });
                    });
                    it("charges $scope.errors if something goes wrong", (done) => {
                        adhUserMock.register.and.returnValue(q.reject([{description: "error"}]));
                        scopeMock.register().then(() => {
                            expect(scopeMock.errors.length).toBe(1);
                            done();
                        });
                    });
                });
            });
        });

        describe("indicatorDirective", () => {
            var directive;
            var adhConfigMock;
            var adhResourceAreaMock;

            beforeEach(() => {
                adhConfigMock = {
                    pkg_path: "mock",
                    root_path: "mock",
                    ws_url: "mock",
                    embedded: true
                };
                adhResourceAreaMock = jasmine.createSpyObj("adhResourceArea", ["has"]);
                adhResourceAreaMock.has.and.returnValue(false);
                directive = AdhUserViews.indicatorDirective(adhConfigMock, adhResourceAreaMock, null, adhPermissionsMock, null);
            });

            describe("controller", () => {
                var controller;
                var scopeMock;
                var adhUserMock;

                beforeEach(() => {
                    scopeMock = {};
                    adhUserMock = jasmine.createSpyObj("adhUserMock", ["logOut"]);
                    controller = <any>(directive.controller[3]);
                    controller(adhUserMock, null, scopeMock);
                });

                describe("logOut", () => {
                    it("calls adhUser.logOut", () => {
                        scopeMock.logOut();
                        expect(adhUserMock.logOut).toHaveBeenCalled();
                    });
                });
            });
        });
    });
};
