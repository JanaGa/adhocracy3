/// <reference path="../../../lib/DefinitelyTyped/underscore/underscore.d.ts"/>

import _ = require("underscore");

import Util = require("../Util/Util");
import AdhHttp = require("../Http/Http");
import AdhConfig = require("../Config/Config");
import AdhWebSocket = require("../WebSocket/WebSocket");

import Resources = require("../../Resources");

var pkgLocation = "/Proposal";

/**
 * contents of the resource with view mode.
 */
interface DetailScope<Data> extends ng.IScope {
    viewmode : string;
    content : Resources.Content<Data>;
}

interface DetailRefScope<Data> extends DetailScope<Data> {
    ref : string;
}

interface IProposalVersionDetailScope<Data> extends DetailScope<Data> {
    list : () => void;
    display : () => void;
    edit : () => void;
    reset : () => void;
    commit : () => void;
}

export class ProposalDetail {
    public createDirective() {
        return {
            restrict: "E",
            template: "<adh-proposal-version-detail data-content=\"content\" data-viewmode=\"list\"></adh-proposal-version-detail>",
            scope: {
                path: "="
            },
            controller: ["adhHttp", "adhWebSocket", "$scope", (adhHttp, adhWebSocket, $scope) => {
                var wsHandle;

                var fetchAndUpdateContent = (itemPath : string) : void => {
                    adhHttp.get(itemPath + "/LAST")
                        .then((tag) => tag.data["adhocracy.sheets.tags.ITag"].elements[0])
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
    public static templateUrl : string = "Resources/IProposalVersion/Detail.html";

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
            controller: ["adhHttp", "$scope", (
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

                $scope.reset = () => {
                    adhHttp.get($scope.content.path).then((content) => {
                        $scope.content = content;
                    });
                    $scope.viewmode = "display";
                };

                $scope.commit = () => {
                    adhHttp.postNewVersion($scope.content.path, $scope.content);

                    $scope.$broadcast("commit");
                    $scope.viewmode = "display";
                };
            }]
        };
    }
}

export class ProposalVersionEdit {

    public createDirective(adhConfig : AdhConfig.Type) {

        return {
            restrict: "E",
            templateUrl: adhConfig.pkg_path + pkgLocation + "/templates/Resources/IProposalVersion/Edit.html",
            scope: {
                content: "="
            }
        };
    }
}

export class ProposalVersionNew {

    public createDirective(adhHttp : ng.IHttpService, adhConfig : AdhConfig.Type, adhProposal : Service) {

        return {
            restrict: "E",
            templateUrl: adhConfig.pkg_path + pkgLocation + "/templates/Resources/IProposalVersion/New.html",
            scope: {
                onNewProposal: "="
            },
            controller: ["$scope", ($scope) => {
                $scope.proposalVersion = (new Resources.Resource("adhocracy_sample.resources.proposal.IProposalVersion"))
                    .addIDocument("", "", []);

                $scope.paragraphVersions = [];

                $scope.addParagraphVersion = () => {
                    $scope.paragraphVersions.push(new Resources.Resource("adhocracy_sample.resources.paragraph.IParagraphVersion")
                                                  .addIParagraph(""));
                };

                $scope.commit = () => {
                    adhProposal.postProposalWithParagraphs($scope.proposalVersion, $scope.paragraphVersions).then((resp) => {
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
            templateUrl: adhConfig.pkg_path + pkgLocation + "/templates/Resources/ISectionVersion/Detail.html",
            compile: (element) => recursionHelper.compile(element),
            scope: {
                ref: "=",
                viewmode: "="
            },
            controller: ["adhHttp", "$scope", (
                adhHttp : AdhHttp.Service<Resources.Content<Resources.HasISectionSheet>>,
                $scope : DetailRefScope<Resources.HasISectionSheet>
            ) : void => {
                var commit = (event, ...args) => {
                    adhHttp.postNewVersion($scope.content.path, $scope.content);
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
            templateUrl: adhConfig.pkg_path + pkgLocation + "/templates/Resources/IParagraphVersion/Detail.html",
            scope: {
                ref: "=",
                viewmode: "="
            },
            controller: ["adhHttp", "$scope", (
                adhHttp : AdhHttp.Service<Resources.Content<Resources.HasIParagraphSheet>>,
                $scope : DetailRefScope<Resources.HasIParagraphSheet>
            ) : void => {
                var commit = (event, ...args) => {
                    adhHttp.postNewVersion($scope.content.path, $scope.content);
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

export class DocumentSheetEdit {

    public createDirective(adhHttp, $q, adhConfig: AdhConfig.Type) {
        return {
            restrict: "E",
            templateUrl: adhConfig.pkg_path + pkgLocation + "/templates/Sheets/IDocument/Edit.html",
            scope: {
                sheet: "="
            },
            controller: ["$scope", ($scope) => {
                var versionPromises = $scope.sheet.elements.map((path) =>
                    adhHttp.get(decodeURIComponent(path))
                        .then((resp) => resp.data)
                );

                $q.all(versionPromises).then((versions) =>
                    $scope.sectionVersions = versions
                );
            }]
        };
    }
}

export class DocumentSheetShow {

    public createDirective (adhConfig : AdhConfig.Type) {
        return {
            restrict: "E",
            templateUrl: adhConfig.pkg_path + pkgLocation + "/templates/Sheets/IDocument/Show.html",
            scope: {
                sheet: "="
            }
        };
    }
}

export class ParagraphSheetEdit {
    public createDirective (adhConfig : AdhConfig.Type) {
        return {
            restrict: "E",
            templateUrl: adhConfig.pkg_path + pkgLocation + "/templates/Sheets/IParagraph/Edit.html",
            scope: {
                sheet: "="
            }
        };
    }
}

export class Service {
    constructor(private adhHttp : AdhHttp.Service<any>, private $q : ng.IQService) {}

    getNewestVersionPath(path : string) : ng.IPromise<any> {
        // FIXME conceptually, there is no single newest version.  Versions have a tree
        // structure and there can be many leafs to that tree.  This is not a technical
        // issue but a concept issue.  For now, we use the first leaf.
        return this.adhHttp.get(path + "/LAST")
            .then((tag) => tag.data["adhocracy.sheets.tags.ITag"].elements[0]);
    }

    postProposal(path : string, name : string, scope : {proposal? : any}) : ng.IPromise<void> {
        return this.adhHttp.postToPool(path, new Resources.Proposal(name))
            .then((ret) => { scope.proposal = ret; });
    }

    postSection(path : string, name : string, scope : {section? : any}) : ng.IPromise<void> {
        return this.adhHttp.postToPool(path, new Resources.Section(name))
            .then((ret) => { scope.section = ret; });
    }

    postParagraph(path : string, name : string, scope : {paragraphs}) : ng.IPromise<void> {
        return this.adhHttp.postToPool(path, new Resources.Paragraph(name))
            .then((ret) => { scope.paragraphs[name] = ret; });
    }

    postParagraphs(path : string, names : string[], scope) : ng.IPromise<void> {
        var _self = this;

        // we need to post the paragraph versions one after another in order to guarantee
        // the right order
        if (names.length > 0) {
            return _self.postParagraph(path, names[0], scope)
                .then(() => _self.postParagraphs(path, names.slice(1), scope));
        } else {
            return _self.$q.when();
        }
    }

    postVersion(path : string, data) : ng.IPromise<any> {
        var _self = this;
        return _self.getNewestVersionPath(path)
            .then((versionPath) => _self.adhHttp.postNewVersion(versionPath, data));
    }

    postProposalVersion(proposal, data, sections, scope) : ng.IPromise<void> {
        var _self = this;
        return _self.$q.all(sections.map((section) => _self.getNewestVersionPath(section.path)))
            .then((sectionVersionPaths) => {
                var _data = Util.deepcp(data);
                _data.data["adhocracy.sheets.document.IDocument"].elements = sectionVersionPaths;
                return _self.postVersion(proposal.path, _data);
            });
    }

    postSectionVersion(section, data, paragraphs, scope) : ng.IPromise<void> {
        var _self = this;
        return _self.$q.all(paragraphs.map((paragraph) => _self.getNewestVersionPath(paragraph.path)))
            .then((paragraphVersionPaths) => {
                var _data = Util.deepcp(data);
                _data.data["adhocracy.sheets.document.ISection"].elements = paragraphVersionPaths;
                return _self.postVersion(section.path, _data);
            });
    }

    postParagraphVersion(paragraph, data, scope : {proposal : any}) : ng.IPromise<void> {
        var _self = this;
        return _self.getNewestVersionPath(scope.proposal.path)
            .then((proposalVersionPath) => {
                var _data = Util.deepcp(data);
                _data.root_versions = [proposalVersionPath];
                return _self.postVersion(paragraph.path, _data);
            });
    }

    postParagraphVersions(paragraphs : any[], datas : any[], scope) : ng.IPromise<void> {
        var _self = this;

        // we need to post the paragraph versions one after another in order to guarantee
        // that the final section version contains all new proposal versions
        if (paragraphs.length > 0) {
            return _self.postParagraphVersion(paragraphs[0], datas[0], scope)
                .then(() => _self.postParagraphVersions(paragraphs.slice(1), datas.slice(1), scope));
        } else {
            return _self.$q.when();
        }
    }

    public postProposalWithParagraphs(proposalVersion : Resources.PartialIProposalVersion, paragraphVersions) {
        var _self = this;

        var sectionVersion = new Resources.Resource("adhocracy_sample.resources.section.ISectionVersion");
        sectionVersion.addISection("single section", []);

        var name = proposalVersion.data["adhocracy.sheets.document.IDocument"].title;
        name = Util.normalizeName(name);

        var scope : {proposal? : any; section? : any; paragraphs : {}} = {
            paragraphs: {}
        };

        return _self.postProposal("/adhocracy", name, scope)
            .then(() => _self.postSection(
                scope.proposal.path,
                "section",
                scope
            ))
            .then(() => _self.postParagraphs(
                scope.proposal.path,
                paragraphVersions.map((paragraphVersion, i) => "paragraph" + i),
                scope
            ))
            .then(() => _self.postProposalVersion(
                scope.proposal,
                proposalVersion,
                [scope.section],
                scope
            ))
            .then(() => _self.postSectionVersion(
                scope.section,
                sectionVersion,
                _.values(scope.paragraphs),
                scope
            ))
            .then(() => _self.postParagraphVersions(
                paragraphVersions.map((paragraphVersion, i) => scope.paragraphs["paragraph" + i]),
                paragraphVersions,
                scope
            ))

            // return the latest proposal Version
            .then(() => _self.getNewestVersionPath(scope.proposal.path))
            .then((proposalVersionPath) => _self.adhHttp.get(proposalVersionPath));
    }
};
