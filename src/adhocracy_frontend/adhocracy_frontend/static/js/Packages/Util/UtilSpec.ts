/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>

import JasmineHelpers = require("../../JasmineHelpers");

import AdhUtil = require("./Util");

export var register = () => {
    describe("Util", () => {
        describe("cutArray", () => {
            it("removes single items", () => {
                expect(AdhUtil.cutArray([1, 2, 3, 4], 0)).toEqual([2, 3, 4]);
                expect(AdhUtil.cutArray([1, 2, 3, 4], 1)).toEqual([1, 3, 4]);
                expect(AdhUtil.cutArray([1, 2, 3, 4], -1)).toEqual([1, 2, 3]);
                expect(AdhUtil.cutArray([1, 2, 3, 4], -2)).toEqual([1, 2, 4]);
            });
            it("removes single items if 'from' and 'to' are equal", () => {
                expect(AdhUtil.cutArray([1, 2, 3, 4], 0, 0)).toEqual([2, 3, 4]);
                expect(AdhUtil.cutArray([1, 2, 3, 4], 1, 1)).toEqual([1, 3, 4]);
                expect(AdhUtil.cutArray([1, 2, 3, 4], -1, -1)).toEqual([1, 2, 3]);
                expect(AdhUtil.cutArray([1, 2, 3, 4], -2, -2)).toEqual([1, 2, 4]);
            });
            it("removes ranges", () => {
                expect(AdhUtil.cutArray([1, 2, 3, 4], 0, -1)).toEqual([]);
                expect(AdhUtil.cutArray([1, 2, 3, 4], 0, 3)).toEqual([]);
                expect(AdhUtil.cutArray([1, 2, 3, 4], 1, 3)).toEqual([1]);
                expect(AdhUtil.cutArray([1, 2, 3, 4], 0, 2)).toEqual([4]);
                expect(AdhUtil.cutArray([1, 2, 3, 4], 1, -2)).toEqual([1, 4]);
                expect(AdhUtil.cutArray([1, 2, 3, 4], -3, -2)).toEqual([1, 4]);
            });
        });

        describe("isArrayMember", () => {
            var isArrayMember = AdhUtil.isArrayMember;

            it("finds nothing in empty array.", () => {
                expect(isArrayMember(0, [])).toBe(false);
            });
            it("finds array members if they are present at pos [0].", () => {
                expect(isArrayMember("wef", ["wef", null, 3])).toBe(true);
            });
            it("finds array members if they are present at pos [end].", () => {
                expect(isArrayMember("wef", [null, "wef"])).toBe(true);
            });
            it("finds array members if they are present in between.", () => {
                expect(isArrayMember("wef", [true, "wef", null, 3])).toBe(true);
            });
            it("does not find array members if they are not present.", () => {
                expect(isArrayMember("wef", ["woff", null, 3])).toBe(false);
            });
            it("works on other base types.", () => {
                expect(isArrayMember(true, [true])).toBe(true);
                expect(isArrayMember(false, [true])).toBe(false);
                expect(isArrayMember(1, [1])).toBe(true);
                expect(isArrayMember(0, [1])).toBe(false);
            });
            it("works on null.", () => {
                expect(isArrayMember(null, [null])).toBe(true);
                expect(isArrayMember(null, [3])).toBe(false);
            });
            it("null is not member of ['null'].", () => {
                expect(isArrayMember(null, ["null"])).toBe(false);
            });
            it("returns false for array properties that are not array items (such as length)", () => {
                expect(AdhUtil.isArrayMember("length", ["hay", "stack"])).toBe(false);
                expect(AdhUtil.isArrayMember(0, ["hay", "stack"])).toBe(false);
            });
        });

        describe("trickle", () => {
            xit("calls function on every arg in array exactly once within the given timeout.", () => {
                expect(false).toBe(true);

                // there is a timeout mock object in jasmine, but any
                // test of this function would mostly test that it is
                // implemented *in a specific* way, which sais nothing
                // about whether it is implemented *correctly*.
                //
                // `trickle` is a beautiful example of the claim that
                // test coverage is not everything.
            });
        });

        describe("parentPath", () => {
            it("returns '/foo' for '/foo/bar'", () => {
                expect(AdhUtil.parentPath("/foo/bar")).toBe("/foo");
            });
            it("returns '/foo/' for '/foo/bar/'", () => {
                expect(AdhUtil.parentPath("/foo/bar/")).toBe("/foo/");
            });
            it("returns '/' for '/'", () => {
                expect(AdhUtil.parentPath("/")).toBe("/");
            });
            it("returns '/' for 'bla'", () => {
                expect(AdhUtil.parentPath("bla")).toBe("/");
            });
            it("returns '/' for ''", () => {
                expect(AdhUtil.parentPath("")).toBe("/");
            });
        });

        describe("normalizeName", () => {
            it("is idempotent", () => {
                ["asdkj", "#!8 sajd ksalkjad\n", "foo bar", "Foo Bar", "foo_bar"].forEach((s) => {
                    var normalized = AdhUtil.normalizeName(s);
                    expect(AdhUtil.normalizeName(normalized)).toBe(normalized);
                });
            });

            it("preserves ascii", () => {
                expect(AdhUtil.normalizeName("asdASD123")).toBe("asdASD123");
            });

            it("replaces german umlauts", () => {
                expect(AdhUtil.normalizeName("äüÄÖß")).toBe("aeueAeOess");
            });

            it("replaces spaces by underscores", () => {
                expect(AdhUtil.normalizeName(" ")).toBe("_");
            });

            it("strips chars that are not allowed in an URI component", () => {
                expect(AdhUtil.normalizeName("$%&/?")).toBe("");
            });

            it("strips non-ascii", () => {
                expect(AdhUtil.normalizeName("…")).toBe("");
            });
        });

        describe("formatString", () => {
            it("formats a string", () => {
                expect(AdhUtil.formatString("Hello {0} from {1}", "World", "Bernd")).toBe("Hello World from Bernd");
            });
            it("does not replace {n} if there is no n-th parameter", () => {
                expect(AdhUtil.formatString("Hello {0} from {1}", "World")).toBe("Hello World from {1}");
            });
        });

        describe("escapeNgExp", () => {
            it("wraps the input in single quotes and escapes any single quotes already in there", () => {
                expect(AdhUtil.escapeNgExp("You, me & 'the thing'")).toBe("'You, me & \\'the thing\\''");
            });
        });

        describe("latestVersionsOnly", () => {
            var testCase = [
                "/asd/version2",
                "/asd/version3",
                "/foo/version1",
                "/bar/version1",
                "/asd/version1",
                "/foo/version2"
            ];

            it("returns only the most recent versions from the adhocracy_core.sheets.comment.ICommentable sheet", () => {
                jasmine.addMatchers(JasmineHelpers.customMatchers);

                var result = AdhUtil.latestVersionsOnly(testCase);
                (<any>expect(result)).toSetEqual(["/asd/version3", "/foo/version2", "/bar/version1"]);
            });

            it("does not alter the input list", () => {
                AdhUtil.latestVersionsOnly(testCase);
                expect(testCase).toEqual([
                    "/asd/version2",
                    "/asd/version3",
                    "/foo/version1",
                    "/bar/version1",
                    "/asd/version1",
                    "/foo/version2"
                ]);
            });
        });

        describe("sortDagTopologically", () => {

            it("sorts a given dag topologically", () => {
                var dag : AdhUtil.IDag<string> = {
                    "A": {
                        "content": "AA",
                        "incoming": [],
                        "outgoing": ["B", "D"],
                        "done": false
                    },
                    "B": {
                        "content": "BB",
                        "incoming": ["A"],
                        "outgoing": ["C"],
                        "done": false
                    },
                    "C": {
                        "content": "CC",
                        "incoming": ["B"],
                        "outgoing": ["D"],
                        "done": false
                    },
                    "D": {
                        "content": "DD",
                        "incoming": ["A", "C"],
                        "outgoing": [],
                        "done": false
                    }
                };

                var result = AdhUtil.sortDagTopologically(dag, ["A"]);
                expect(result).toEqual(["AA", "BB", "CC", "DD"]);
            });

            it("throws a cycle detected error if the given graph contains cycles", () => {
                var dag : AdhUtil.IDag<string> = {
                    "A": {
                        "content": "AA",
                        "incoming": [],
                        "outgoing": ["B"],
                        "done": false
                    },
                    "B": {
                        "content": "BB",
                        "incoming": ["A", "C"],
                        "outgoing": ["C"],
                        "done": false
                    },
                    "C": {
                        "content": "CC",
                        "incoming": ["B"],
                        "outgoing": ["B"],
                        "done": false
                    }
                };

                expect(() => AdhUtil.sortDagTopologically(dag, ["A"])).toThrow();
            });
        });
    });
};
