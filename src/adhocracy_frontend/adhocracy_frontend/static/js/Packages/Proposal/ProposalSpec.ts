/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>
/// <reference path="../../_all.d.ts"/>

import q = require("q");

import AdhProposal = require("./Proposal");
import AdhPreliminaryNames = require("../../Packages/PreliminaryNames/PreliminaryNames");


var createAdhHttpMock = () => {
    var mock = <any>jasmine.createSpyObj("adhHttpMock", ["get", "options", "postToPool"]);
    mock.get.and.returnValue(q.when({}));
    mock.options.and.returnValue(q.when());
    mock.postToPool.and.returnValue(q.when({}));
    return mock;
};


export var register = () => {
    describe("Proposal", () => {
        describe("Service", () => {
            var adhProposal : AdhProposal.Service;
            var adhHttpMock;
            var scopeTemplate = {
                options: { POST: true },
                paragraphs: {}
            };

            beforeEach(() => {
                adhHttpMock = createAdhHttpMock();
                adhProposal = new AdhProposal.Service(adhHttpMock, new AdhPreliminaryNames(), q);
            });
        });
    });
};
