/// <reference path="./_AdhocracySDK.d.ts"/>

/**
 * AdhocracySDK is not a module and can therefore not be imported.
 * Instead, we use it like an external ("ambient") library - that is,
 * manually.
 *
 * For this reason these tests are disabled by default and
 * _AdhocracySDK.d.ts is included in the source tree.
 *
 * FIXME: move to from ../js/ to ../sdk/, so that the special
 * circumstances will become more appearent.
 */

export var register = () => {
    xdescribe("AdhocracySDK", () => {
        it("dummy", () => {
            expect(adhocracy).toBeDefined();
        });
    });
};
