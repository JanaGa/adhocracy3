/// <reference path="../../../lib2/types/jasmine.d.ts"/>

import * as q from "q";

import * as AdhHttp from "./Http";
import * as AdhPreliminaryNames from "../PreliminaryNames/PreliminaryNames";

import * as ResourcesBase from "../../ResourcesBase";

import RIParagraph from "../../Resources_/adhocracy_core/resources/paragraph/IParagraph";
import * as SITags from "../../Resources_/adhocracy_core/sheets/tags/ITags";

import * as Convert from "./Convert";
import * as Error from "./Error";


var mkHttpMock = (adhPreliminaryNames : AdhPreliminaryNames.Service) => {
    var mock = jasmine.createSpy("$httpMock");

    var response = new RIParagraph({ preliminaryNames: adhPreliminaryNames });

    (<any>mock).get = jasmine.createSpy("$httpMock.get").and.returnValue(q.when({ data: response }));
    (<any>mock).post = jasmine.createSpy("$httpMock.post").and.returnValue(q.when({ data: response }));
    (<any>mock).put = jasmine.createSpy("$httpMock.put").and.returnValue(q.when({ data: response }));

    return mock;
};

var mkTimeoutMock = () => {
    return jasmine.createSpy("timeoutMock").and.callFake((fn, ms, invokeApply) => fn());
};

var mkAdhMetaApiMock = () => {
    var mock = {
        objBefore: {
            content_type: RIParagraph.content_type,
            data: {
                readWriteSheet: {
                    readOnlyField: 3,
                    readWriteField: 8
                },
                readOnlySheet: {
                    readOnlyField2: 9
                }
            }
        },

        objAfter: {
            content_type: RIParagraph.content_type,
            data: {
                readWriteSheet: {
                    readWriteField: 8
                }
            }
        },

        sheetExists: () => true,
        fieldExists: () => true,

        // used by exportResource.
        field: (sheet, field) => {
            switch (sheet + "/" + field) {
            case "readWriteSheet/readOnlyField":
                return { editable: false };
            case "readWriteSheet/readWriteField":
                return { editable: true };
            case "readOnlySheet/readOnlyField2":
                return { editable: false };
            default:
                return { editable: true };  // by default, don't delete anything.
            }
        }
    };

    spyOn(mock, "sheetExists").and.callThrough();
    spyOn(mock, "fieldExists").and.callThrough();
    spyOn(mock, "field").and.callThrough();

    return mock;
};


export var register = () => {
    describe("Http", () => {
        describe("Service", () => {
            var adhPreliminaryNames;
            var $httpMock;
            var $timeoutMock;
            var adhMetaApiMock;
            var adhConfigMock;
            var adhCacheMock;
            var adhCredentialsMock;
            var adhHttp : AdhHttp.Service<any>;

            beforeEach(() => {
                adhPreliminaryNames = new AdhPreliminaryNames.Service();
                $httpMock = mkHttpMock(adhPreliminaryNames);
                $timeoutMock = mkTimeoutMock();
                adhMetaApiMock = mkAdhMetaApiMock();
                adhConfigMock = { rest_url: "" };
                adhCacheMock = {
                    invalidate: (path) => undefined,
                    invalidateAll: () => undefined,
                    invalidateUpdated: (updated, posted) => undefined,
                    memoize: (path, subkey, closure) => closure()
                };
                adhCredentialsMock = {
                    ready: q.when(true)
                };
                adhHttp = new AdhHttp.Service(
                    $httpMock, <any>q, $timeoutMock, adhCredentialsMock, adhMetaApiMock, adhPreliminaryNames, adhConfigMock, adhCacheMock);
            });

            describe("options", () => {
                it("calls $http().", (done) => {
                    $httpMock.and.returnValue(q.when({ data: {} }));
                    adhHttp.options("/some/path").then(
                        () => {
                            expect($httpMock).toHaveBeenCalled();
                            done();
                        },
                        (msg) => {
                            expect(msg).toBe(false);
                            done();
                        }
                    );
                });
                it("returns a streamlined, aggregated OPTIONS structure.", (done) => {
                    $httpMock.and.returnValue(q.when({ data: {
                        OPTIONS: { arg: 3, bloo: false },
                        GET: true,
                        PUT: false
                    }}));
                    adhHttp.options("/some/path").then(
                        (options) => {
                            expect(options).toEqual({
                                OPTIONS: true,
                                PUT: false,
                                GET: true,
                                POST: false,
                                HEAD: false,
                                DELETE: false,
                                hide: false,
                                canPost: jasmine.any(Function),
                                canPut: jasmine.any(Function)
                            });
                            done();
                        },
                        (msg) => {
                            expect(msg).toBe(false);
                        });
                });
                it("crashes if data field is missing in response.", (done) => {
                    $httpMock.and.returnValue(q.when({ doto: false }));
                    adhHttp.options("/some/path").then(
                        () => {
                            expect("should have thrown").toBe(false);
                            done();
                        },
                        (msg) => {
                            expect(true).toBe(true);
                            done();
                        });
                });
            });
            describe("get", () => {
                it("calls $http.get", (done) => {
                    adhHttp.get("/some/path").then(
                        () => {
                            expect($httpMock.get).toHaveBeenCalled();
                            done();
                        },
                        (msg) => {
                            expect(msg).toBe(false);
                            done();
                        }
                    );
                });
            });
            describe("post", () => {
                it("calls $http.post", (done) => {
                    adhHttp.post("/some/path", {content_type: RIParagraph.content_type, data: {}}).then(
                        () => {
                            expect($httpMock.post).toHaveBeenCalled();
                            done();
                        },
                        (msg) => {
                            expect(msg).toBe(false);
                            done();
                        }
                    );
                });
            });
            describe("put", () => {
                it("calls $http.put", (done) => {
                    adhHttp.put("/some/path", {content_type: RIParagraph.content_type, data: {}}).then(
                        () => {
                            expect($httpMock.put).toHaveBeenCalled();
                            done();
                        },
                        (msg) => {
                            expect(msg).toBe(false);
                            done();
                        }
                    );
                });
            });
            describe("getNewestVersionPathNoFork", () => {
                it("promises the unique path from the LAST tag", (done) => {
                    var path = "path/";
                    var returnPath1 = "path1/";

                    var dag = new RIParagraph({ preliminaryNames: adhPreliminaryNames });
                    dag.data["adhocracy_core.sheets.tags.ITags"] = new SITags.Sheet({ LAST: returnPath1 });
                    $httpMock.get.and.returnValue(q.when({ data: dag }));

                    adhHttp.getNewestVersionPathNoFork(path).then(
                        (ret) => {
                            expect(ret).toBe(returnPath1);
                            expect($httpMock.get).toHaveBeenCalledWith(path, {
                                params: undefined,
                                headers: {}
                            });
                            done();
                        },
                        (msg) => {
                            // on exception: report the error and fail.
                            expect(msg).toBe(false);
                            done();
                        }
                    );
                });
            });
            describe("postNewVersionNoFork", () => {
                var noForkError = {
                    description: "No fork allowed",
                    location: "body",
                    name: "data.adhocracy_core.sheets.versions.IVersionable.follows"
                };

                it("posts to parent pool, adds IVersionable sheet with correct follows field", (done) => {
                    adhHttp.postNewVersionNoFork("/ome/path", {content_type: RIParagraph.content_type, data: {}}).then(
                        (resource) => {
                            expect($httpMock.post).toHaveBeenCalledWith("/ome", {
                                content_type: RIParagraph.content_type,
                                data: {
                                    "adhocracy_core.sheets.versions.IVersionable": {
                                        follows: ["/ome/path"]
                                    }
                                }
                            }, {
                                headers: {}
                            });
                            done();
                        },
                        (msg) => {
                            expect(msg).toBe(false);
                            done();
                        }
                    );
                });

                it("catches single \"no-fork\" exceptions and retries 4 more times.", (done) => {
                    var error = {
                        status: "error",
                        errors: [noForkError]
                    };
                    $httpMock.post.and.returnValue(q.reject({ data: error }));

                    adhHttp.getNewestVersionPathNoFork = (<any>jasmine.createSpy("getNewestVersionPathNoForkSpy"))
                        .and.returnValue(q.when("next_head"));

                    adhHttp.postNewVersionNoFork("/somee/path", {content_type: RIParagraph.content_type, data: {}}).then(
                        () => {
                            expect("postNewVersionNoFork should have failed!").toBe(false);
                            done();
                        },
                        (msg) => {
                            expect($httpMock.post.calls.count()).toEqual(5);
                            done();
                        }
                    );
                });

                it("does NOT catch any other (lists of) exceptions (more precisely: rethrows them).", (done) => {
                    var error = {
                        status: "error",
                        errors: [{name: "i am not a no-fork error", location: "", description: ""}]
                    };
                    $httpMock.post.and.returnValue(q.reject({ data: error }));

                    adhHttp.postNewVersionNoFork("/somee/path", {content_type: RIParagraph.content_type, data: {}}).then(
                        () => {
                            expect("postNewVersionNoFork should have failed!").toBe(false);
                            done();
                        },
                        (msg) => {
                            expect($httpMock.post.calls.count()).toEqual(1);
                            done();
                        }
                    );
                });

                it("adds a root_versions field if rootVersions is passed", (done) => {
                    adhHttp.postNewVersionNoFork("/somee/path", {content_type: RIParagraph.content_type, data: {}}, ["foo", "bar"]).then(
                        () => {
                            expect($httpMock.post).toHaveBeenCalledWith("/somee", {
                                content_type: RIParagraph.content_type,
                                data: {
                                    "adhocracy_core.sheets.versions.IVersionable": {
                                        follows: ["/somee/path"]
                                    }
                                },
                                root_versions: ["foo", "bar"]
                            }, {
                                headers: {}
                            });
                            done();
                        },
                        (msg) => {
                            expect(msg).toBe(false);
                            done();
                        }
                    );
                });

                it("Calls timeout; then calls post again with new HEAD as predecessor version.", (done) => {
                    var error = {
                        status: "error",
                        errors: [noForkError]
                    };

                    var newHead = "new_head";
                    var dag = new RIParagraph({ preliminaryNames: adhPreliminaryNames });
                    dag.data["adhocracy_core.sheets.tags.ITags"] = new SITags.Sheet({ FIRST: undefined,
                                                                                      LAST: newHead
                                                                                    });


                    var postResponses = [q.reject({ data: error }), q.when({ data: dag })].reverse();

                    $httpMock.post.and.callFake(() => postResponses.pop());
                    $httpMock.get.and.returnValue(q.when({ data: dag }));

                    spyOn(adhHttp, "getNewestVersionPathNoFork").and.callThrough();

                    adhHttp.postNewVersionNoFork("/somee/path", {content_type: RIParagraph.content_type, data: {}}).then(
                        () => {
                            expect($httpMock.post.calls.count()).toEqual(2);

                            var extractFollowsRef = (resource) => {
                                try {
                                    var follows = resource.data["adhocracy_core.sheets.versions.IVersionable"].follows;
                                    if (follows.length !== 1) {
                                        throw "blä!";
                                    }
                                    return follows[0];
                                } catch (e) {
                                    return false;
                                }
                            };
                            expect(extractFollowsRef($httpMock.post.calls.argsFor(1)[1])).toEqual(newHead);
                            expect($httpMock.get.calls.count()).toEqual(1);
                            expect(adhHttp.getNewestVersionPathNoFork).toHaveBeenCalledWith("/somee");
                            expect($timeoutMock.calls.count()).toEqual(1);
                            done();
                        },
                        (msg) => {
                            expect(msg).toBe(false);
                            done();
                        }
                    );
                });
            });

            describe("postToPool", () => {
                it("calls $http.post", (done) => {
                    adhHttp.postToPool("/some/path", {content_type: RIParagraph.content_type, data: {}}).then(
                        () => {
                            expect($httpMock.post).toHaveBeenCalled();
                            done();
                        },
                        (msg) => {
                            expect(msg).toBe(false);
                            done();
                        }
                    );
                });
            });
            describe("resolve", () => {
                it("gets the resource if called with a path", (done) => {
                    var path = "/some/path";
                    var resource = {
                        content_type: "mock2",
                        data: {}
                    };
                    adhHttp.get = <any>(jasmine.createSpy("adhHttp.get")
                        .and.returnValue(q.when(resource)));

                    adhHttp.resolve(path).then((ret) => {
                        expect(ret).toEqual(resource);
                        expect(adhHttp.get).toHaveBeenCalledWith(path);
                        done();
                    });
                });
                it("promises the resource if called with a resource", (done) => {
                    var resource = {
                        content_type: "mock2",
                        data: {}
                    };

                    adhHttp.resolve(resource).then((ret) => {
                        expect(ret).toEqual(resource);
                        done();
                    });
                });
            });
            describe("withTransaction", () => {
                var get;
                var put;
                var post1;
                var post2;
                var delete1;
                var get2;
                var request;
                var response;
                var _httpTrans;

                beforeEach((done) => {
                    $httpMock.post.and.returnValue(q.when({data: {
                        responses: [
                            {body: {content_type: RIParagraph.content_type, path: "get response"}},
                            {body: {content_type: RIParagraph.content_type, path: "put response"}},
                            {body: {content_type: RIParagraph.content_type, path: "post1 response"}},
                            {body: {content_type: RIParagraph.content_type, path: "post2 response"}},
                            {body: {}},
                            {body: {content_type: RIParagraph.content_type, path: "get2 response"}}
                        ],
                        updated_resources: {
                            changed_descendants: [],
                            created: [],
                            modified: [],
                            removed: []
                        }
                    }}));

                    adhHttp.withTransaction((httpTrans) => {
                        _httpTrans = httpTrans;

                        get = httpTrans.get("/get/path");
                        put = httpTrans.put("/put/path", <any>{
                            content_type: RIParagraph.content_type
                        });
                        post1 = httpTrans.post("/post/path/1", <any>{
                            content_type: RIParagraph.content_type
                        });
                        post2 = httpTrans.post("/post/path/2", <any>{
                            content_type: RIParagraph.content_type
                        });
                        delete1 = httpTrans.delete("/delete/path");
                        get2 = httpTrans.get(post1.path);
                        return httpTrans.commit();
                    }).then(
                        (_response) => {
                            response = _response;
                            done();
                        },
                        (error) => {
                            throw "This should not happen";
                        }
                    );
                });

                it("posts to /batch", () => {
                    expect($httpMock.post).toHaveBeenCalled();
                    var args = $httpMock.post.calls.mostRecent().args;
                    expect(args[0]).toBe("/batch");
                    request = args[1];
                });

                it("maps preliminary data to responses via `index`", () => {
                    expect(response[get.index].path).toBe("get response");
                    expect(response[put.index].path).toBe("put response");
                    expect(response[post1.index].path).toBe("post1 response");
                    expect(response[post2.index].path).toBe("post2 response");
                    expect(response[get2.index].path).toBe("get2 response");
                });

                it("throws if you try to use the transaction after commit", () => {
                    expect(() => _httpTrans.get("/some/path")).toThrow();
                });

                describe("post", () => {
                    it("assigns different preliminary paths to different post requests", () => {
                        expect(post1.path).not.toEqual(post2.path);
                    });

                    it("assigns preliminary first_version_paths on post requests", () => {
                        expect(post1.first_version_path).toBeDefined();
                    });

                    it("prefixes preliminary paths with a single '@'", () => {
                        expect(post1.path[0]).toBe("@");
                        expect(post1.path[1]).not.toBe("@");
                    });

                    it("prefixes preliminary first_version_paths with a single '@'", () => {
                        expect(post1.first_version_path[0]).toBe("@");
                        expect(post1.first_version_path[1]).not.toBe("@");
                    });

                    it("adds a result_path to post requests", () => {
                        expect(request[post1.index].result_path).toBeDefined();
                        expect(request[post1.index].result_path).toBe(post1.path);

                        expect(request[post2.index].result_path).toBeDefined();
                        expect(request[post2.index].result_path).toBe(post2.path);
                    });
                });

                describe("delete", () => {
                    it("uses the DELETE method", () => {
                        expect(request[delete1.index].body).not.toBeDefined();
                        expect(request[delete1.index].method).toBe("DELETE");
                    });

                    it("the response path is based on the request, as the response body is empty", () => {
                        expect(response[delete1.index].path).toBe("/delete/path");
                    });
                });
            });
        });

        describe("importResource", () => {
            var adhCacheMock;

            beforeEach(() => {
                adhCacheMock = {
                    invalidate: (path) => undefined,
                    invalidateAll: () => undefined,
                    invalidateUpdated: (updated, posted) => undefined,
                    memoize: (path, subkey, closure) => closure()
                };
            });

            it("returns response.data if it is an object", () => {
                var obj : ResourcesBase.IResource = <any>{
                    content_type: "adhocracy_core.resources.pool.IBasicPool",
                    path: "p",
                    data: {}
                };
                var response = {
                    data: obj
                };
                var adhMetaApiMock = mkAdhMetaApiMock();
                var adhPreliminaryNames = new AdhPreliminaryNames.Service();
                var imported = () => Convert.importResource(response, <any>adhMetaApiMock, adhPreliminaryNames, adhCacheMock);
                expect(imported().path).toBe(obj.path);
            });
            it("throws if response.data is not an object", () => {
                var obj = <any>"foobar";
                var response = {
                    data: obj
                };
                var adhMetaApiMock = mkAdhMetaApiMock();
                var adhPreliminaryNames = new AdhPreliminaryNames.Service();
                var imported = () => Convert.importResource(response, <any>adhMetaApiMock, adhPreliminaryNames, adhCacheMock);
                expect(imported).toThrow();
            });
        });

        describe("exportResource", () => {
            var adhMetaApiMock;

            beforeEach(() => {
                adhMetaApiMock = mkAdhMetaApiMock();
            });

            it("deletes the path", () => {
                expect(Convert.exportResource(adhMetaApiMock, <any>{content_type: RIParagraph.content_type, data: {}, path: "test"}))
                    .toEqual({content_type: RIParagraph.content_type, data: {}});
            });
            it("deletes read-only properties", () => {
                var x = Convert.exportResource(adhMetaApiMock, adhMetaApiMock.objBefore);
                var y = adhMetaApiMock.objAfter;
                expect(x).toEqual(y);  // (yes, this appears to do deep comparison of the entire structure.)
                expect(adhMetaApiMock.field).toHaveBeenCalled();
            });
        });

        var _logBackendError = (name, fn, wrap) => {
            describe(name, () => {
                it("always throws an exception", () => {
                    var backendError = {
                        status: "error",
                        errors: []
                    };
                    expect(() => fn(wrap(backendError))).toThrow();
                });
            });
        };

        _logBackendError(
            "logBackendError",
            AdhHttp.logBackendError,
            (error) => {
                return { data: error };
            }
        );
        _logBackendError(
            "logBackendBatchError",
            Error.logBackendBatchError,
            (error) => {
                return { data: [ {body: error} ]};
            }
        );
    });
};
