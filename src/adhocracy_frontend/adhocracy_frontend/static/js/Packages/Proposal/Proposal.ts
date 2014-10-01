/// <reference path="../../../lib/DefinitelyTyped/lodash/lodash.d.ts"/>

import Util = require("../Util/Util");
import AdhHttp = require("../Http/Http");
import AdhConfig = require("../Config/Config");
import AdhWebSocket = require("../WebSocket/WebSocket");
import AdhTopLevelState = require("../TopLevelState/TopLevelState");
import AdhPreliminaryNames = require("../../Packages/PreliminaryNames/PreliminaryNames");

import Resources = require("../../Resources");

import RIParagraph = require("../../Resources_/adhocracy_core/resources/sample_paragraph/IParagraph");
import RIParagraphVersion = require("../../Resources_/adhocracy_core/resources/sample_paragraph/IParagraphVersion");
import RIProposal = require("../../Resources_/adhocracy_core/resources/sample_proposal/IProposal");
import RIProposalVersion = require("../../Resources_/adhocracy_core/resources/sample_proposal/IProposalVersion");
import RISectionVersion = require("../../Resources_/adhocracy_core/resources/sample_section/ISectionVersion");
import RISection = require("../../Resources_/adhocracy_core/resources/sample_section/ISection");
import SIParagraph = require("../../Resources_/adhocracy_core/sheets/document/IParagraph");
import SISection = require("../../Resources_/adhocracy_core/sheets/document/ISection");
import SIDocument = require("../../Resources_/adhocracy_core/sheets/document/IDocument");
import SIVersionable = require("../../Resources_/adhocracy_core/sheets/versions/IVersionable");

var pkgLocation = "/Proposal";

/**
 * contents of the resource with view mode.
 */
interface DetailScope<Data> extends ng.IScope {
    viewmode : string;
    content : Resources.Content<Data>;
    path : string;
}

interface DetailRefScope<Data> extends DetailScope<Data> {
    ref : string;
}

interface IProposalVersionDetailScope<Data> extends DetailScope<Data> {
    list : () => void;
    display : () => void;
    edit : () => void;
    onCancel : () => void;
    commit : () => void;
    showComments : () => void;
    hideComments : () => void;
}

export class ProposalDetail {
    public createDirective() {
        return {
            restrict: "E",
            template: "<adh-proposal-version-detail data-content=\"content\" data-viewmode=\"list\"></adh-proposal-version-detail>",
            scope: {
                path: "="
            },
            controller: ["adhHttp", "adhWebSocket", "$scope", (
                adhHttp : AdhHttp.Service<any>,
                adhWebSocket : AdhWebSocket.IService,
                $scope : DetailScope<RIProposal>
            ) => {
                var wsHandle;

                var fetchAndUpdateContent = (itemPath : string) : void => {
                    adhHttp.getNewestVersionPathNoFork(itemPath)
                        .then((versionPath) => adhHttp.get(versionPath))
                        .then((content) => {
                            $scope.content = content;
                        });
                };

                var wsHandler = (event : AdhWebSocket.IServerEvent) : void => {
                    fetchAndUpdateContent($scope.path);
                };

                try {
                    if (typeof wsHandle !== "undefined") {
                        adhWebSocket.unregister($scope.path, wsHandle);
                    }
                    wsHandle = adhWebSocket.register($scope.path, wsHandler);

                } catch (e) {
                    console.log(e);
                    console.log("Will continue on resource " + $scope.path + " without server bind.");
                }

                fetchAndUpdateContent($scope.path);
            }]
        };
    }
}

export class ProposalVersionDetail {
    public static templateUrl : string = "Proposal.html";

    public createDirective(adhConfig : AdhConfig.Type) {
        var _self = this;
        var _class = (<any>_self).constructor;

        return {
            restrict: "E",
            templateUrl: adhConfig.pkg_path + pkgLocation + "/templates/" + _class.templateUrl,
            scope: {
                content: "=",
                viewmode: "@"
            },
            controller: ["adhTopLevelState", "adhHttp", "$scope", (
                adhTopLevelState : AdhTopLevelState.TopLevelState,
                adhHttp : AdhHttp.Service<Resources.Content<any>>,
                $scope : IProposalVersionDetailScope<any>
            ) : void => {
                $scope.list = () => {
                    $scope.viewmode = "list";
                };

                $scope.display = () => {
                    $scope.viewmode = "display";
                };

                $scope.edit = () => {
                    $scope.viewmode = "edit";
                };

                $scope.onCancel = () => {
                    adhHttp.get($scope.content.path).then((content) => {
                        $scope.content = content;
                    });
                    $scope.viewmode = "display";
                };

                $scope.commit = () => {
                    adhHttp.postNewVersionNoFork($scope.content.path, $scope.content);

                    $scope.$broadcast("commit");
                    $scope.viewmode = "display";
                };

                $scope.showComments = () => {
                    adhTopLevelState.setContent2Url($scope.content.path);
                    adhTopLevelState.setFocus(2);
                };

                $scope.hideComments = () => {
                    adhTopLevelState.setFocus(1);
                };
            }]
        };
    }
}

interface IScopeProposalVersion {
    content : RIProposalVersion;
    paragraphVersions : RIParagraphVersion[];
    addParagraphVersion : () => void;
    commit : () => void;
    onNewProposal : (any) => void;
    onCancel : () => void;
    poolPath : string;
    viewmode : string;
}

export class ProposalVersionNew {

    public createDirective(adhHttp : ng.IHttpService, adhConfig : AdhConfig.Type, adhProposal : Service) {

        return {
            restrict: "E",
            templateUrl: adhConfig.pkg_path + pkgLocation + "/templates/Proposal.html",
            scope: {
                onNewProposal: "=",
                onCancel: "=",
                poolPath: "@"
            },
            controller: ["$scope", "adhPreliminaryNames", ($scope : IScopeProposalVersion, adhPreliminaryNames : AdhPreliminaryNames) => {
                $scope.viewmode = "edit";

                $scope.content = new RIProposalVersion({preliminaryNames: adhPreliminaryNames});
                $scope.content.data[SIDocument.nick] =
                    new SIDocument.AdhocracyCoreSheetsDocumentIDocument({
                        title: "",
                        description: "",
                        elements: []
                    });
                $scope.paragraphVersions = [];

                $scope.addParagraphVersion = () => {
                    var pv = new RIParagraphVersion({preliminaryNames: adhPreliminaryNames});
                    pv.data[SIParagraph.nick] =
                        new SIParagraph.AdhocracyCoreSheetsDocumentIParagraph({
                            content: ""
                        });
                    $scope.paragraphVersions.push(pv);
                };

                $scope.commit = () => {
                    adhProposal.postProposalWithParagraphs($scope.poolPath, $scope.content, $scope.paragraphVersions)
                        .then((resp) => {
                            adhHttp.get(resp.path).then((respGet) => {
                                $scope.onNewProposal(respGet);
                            });
                        });
                };
            }]
        };
    }
}

export class SectionVersionDetail {

    public createDirective(adhConfig : AdhConfig.Type, recursionHelper) {

        return {
            restrict: "E",
            templateUrl: adhConfig.pkg_path + pkgLocation + "/templates/Section.html",
            compile: (element) => recursionHelper.compile(element),
            scope: {
                ref: "=",
                viewmode: "="
            },
            controller: ["adhHttp", "$scope", (
                adhHttp : AdhHttp.Service<Resources.Content<SISection.HasAdhocracyCoreSheetsDocumentISection>>,
                $scope : DetailRefScope<SISection.HasAdhocracyCoreSheetsDocumentISection>
            ) : void => {
                var commit = (event, ...args) => {
                    adhHttp.postNewVersionNoFork($scope.content.path, $scope.content);
                };

                // keep pristine copy in sync with cache.  FIXME: this should be done in one gulp with postNewVersion
                adhHttp.get($scope.ref).then((content) => {
                    $scope.content = content;
                });

                // save working copy on 'commit' event from containing document.
                $scope.$on("commit", commit);
            }]
        };
    }
}

export class ParagraphVersionDetail {

    public createDirective(adhConfig : AdhConfig.Type) {

        return {
            restrict: "E",
            templateUrl: adhConfig.pkg_path + pkgLocation + "/templates/Paragraph.html",
            scope: {
                ref: "=",
                viewmode: "="
            },
            controller: ["adhHttp", "$scope", (
                adhHttp : AdhHttp.Service<Resources.Content<SIParagraph.HasAdhocracyCoreSheetsDocumentIParagraph>>,
                $scope : DetailRefScope<SIParagraph.HasAdhocracyCoreSheetsDocumentIParagraph>
            ) : void => {
                var commit = (event, ...args) => {
                    adhHttp.postNewVersionNoFork($scope.content.path, $scope.content);
                };

                // keep pristine copy in sync with cache.  FIXME: this should be done in one gulp with postNewVersion
                adhHttp.get($scope.ref).then((content) => {
                    $scope.content = content;
                });

                // save working copy on 'commit' event from containing document.
                $scope.$on("commit", commit);
            }]
        };
    }
}

export class Service {
    constructor(
        private adhHttp : AdhHttp.Service<any>,
        private adhPreliminaryNames : AdhPreliminaryNames,
        private $q : ng.IQService
    ) {}


    public postProposalWithParagraphs(
        poolPath : string,
        proposalVersion : RIProposalVersion,
        paragraphVersions : RIParagraphVersion[]
    ) {
        var _self = this;

        var sectionVersion : RISectionVersion = new RISectionVersion({preliminaryNames: _self.adhPreliminaryNames});
        sectionVersion.data[SISection.nick] =
            new SISection.AdhocracyCoreSheetsDocumentISection({
                title : "single_section",
                elements : [],
                subsections : []
            });

        var name = proposalVersion.data[SIDocument.nick].title;
        name = Util.normalizeName(name);

        // this is the batch-request logic.  it works a bit different
        // from the original logic in that it follows the references
        // down the items and up the versions, rather than going down
        // both.
        //
        // (this comment reference a meeting held earlier today and is
        // meaningless without having been there.  since this function
        // will be refactored away soon, so that should not be a big
        // deal.)

        return _self.adhHttp
            .withTransaction((transaction) : ng.IPromise<Resources.Content<any>> => {
                // items
                var postProposal : AdhHttp.ITransactionResult =
                    transaction.post(poolPath, new RIProposal({preliminaryNames: _self.adhPreliminaryNames, name: name}));
                var postSection : AdhHttp.ITransactionResult =
                    transaction.post(postProposal.path, new RISection({preliminaryNames: _self.adhPreliminaryNames, name: "section"}));
                var postParagraphs : AdhHttp.ITransactionResult[] =
                    paragraphVersions.map((paragraphVersion, i) =>
                        transaction.post(
                            postProposal.path,
                            new RIParagraph({preliminaryNames: _self.adhPreliminaryNames, name: "paragraph" + i})));

                // versions
                var postParagraphVersions = paragraphVersions.map((paragraphVersion, i) => {
                    paragraphVersion.data[SIVersionable.nick] =
                        new SIVersionable.AdhocracyCoreSheetsVersionsIVersionable({
                            follows: [postParagraphs[i].first_version_path]
                        });
                    return transaction.post(postParagraphs[i].path, paragraphVersion);
                });

                sectionVersion.data[SIVersionable.nick] =
                    new SIVersionable.AdhocracyCoreSheetsVersionsIVersionable({
                        follows: [postSection.first_version_path]
                    });
                sectionVersion.data[SISection.nick].elements = postParagraphVersions.map((p) => p.path);
                var postSectionVersion = transaction.post(postSection.path, sectionVersion);

                proposalVersion.data[SIVersionable.nick] =
                    new SIVersionable.AdhocracyCoreSheetsVersionsIVersionable({
                        follows: [postProposal.first_version_path]
                    });
                proposalVersion.data[SIDocument.nick].elements = [postSectionVersion.path];
                var postProposalVersion : AdhHttp.ITransactionResult = transaction.post(postProposal.path, proposalVersion);

                return transaction.commit()
                    .then((responses) : Resources.Content<any> => {
                        // return the latest proposal Version
                        return responses[postProposalVersion.index];
                    });
            });
    }
};
