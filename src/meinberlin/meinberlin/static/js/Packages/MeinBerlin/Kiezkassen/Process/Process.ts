/// <reference path="../../../../../lib/DefinitelyTyped/lodash/lodash.d.ts"/>
/// <reference path="../../../../../lib/DefinitelyTyped/moment/moment.d.ts"/>

import _ = require("lodash");

import AdhConfig = require("..././../Config/Config");
import AdhHttp = require("../../../Http/Http");
import AdhMovingColumns = require("../../../MovingColumns/MovingColumns");
import AdhPermissions = require("../../../Permissions/Permissions");
import AdhTabs = require("../../../Tabs/Tabs");
import AdhTopLevelState = require("../../../TopLevelState/TopLevelState");
import AdhUtil = require("../../../Util/Util");

import SILocationReference = require("../../../../Resources_/adhocracy_core/sheets/geo/ILocationReference");
import SIMultiPolygon = require("../../../../Resources_/adhocracy_core/sheets/geo/IMultiPolygon");
import SITitle = require("../../../../Resources_/adhocracy_core/sheets/title/ITitle");
import SIWorkflow = require("../../../../Resources_/adhocracy_core/sheets/workflow/IWorkflowAssignment");

var pkgLocation = "/MeinBerlin/Kiezkassen/Process";


export var detailDirective = (
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service<any>,
    adhPermissions : AdhPermissions.Service
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Detail.html",
        scope: {
            path: "@"
        },
        require: "^adhMovingColumn",
        link: (scope, element, attrs, column : AdhMovingColumns.MovingColumnController) => {
            scope.shared = column.$scope.shared;
            scope.showMap = (isShowMap : boolean) => {
                scope.shared.isShowMap = isShowMap;
            };
            scope.$watch("path", (value : string) => {
                if (value) {
                    adhHttp.get(value).then((resource) => {
                        var stateName = resource.data[SIWorkflow.nick].workflow_state;
                        scope.currentPhase = resource.data[SIWorkflow.nick].state_data[stateName];

                        var locationUrl = resource.data[SILocationReference.nick].location;
                        adhHttp.get(locationUrl).then((location) => {
                            var polygon = location.data[SIMultiPolygon.nick].coordinates[0][0];
                            scope.polygon =  polygon;
                        });
                    });
                }
            });
            adhPermissions.bindScope(scope, () => scope.path);
        }
    };
};


export var phaseHeaderDirective = (
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service<any>,
    adhTopLevelState : AdhTopLevelState.Service
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/PhaseHeader.html",
        scope: {},
        link: (scope) => {
            var processUrl = adhTopLevelState.get("processUrl");
            adhHttp.get(processUrl).then((resource) => {
                scope.currentPhase = resource.data[SIWorkflow.nick].workflow_state;
                if (resource.data[SIWorkflow.nick].state_data.announce) {
                    scope.phases[0].startDate = resource.data[SIWorkflow.nick].state_data.announce.start_date;
                }
                if (resource.data[SIWorkflow.nick].state_data.participate) {
                    scope.phases[0].endDate = resource.data[SIWorkflow.nick].state_data.participate.start_date;
                    scope.phases[1].startDate = resource.data[SIWorkflow.nick].state_data.participate.start_date;
                }
                if (resource.data[SIWorkflow.nick].state_data.frozen) {
                    scope.phases[1].endDate = resource.data[SIWorkflow.nick].state_data.frozen.start_date;
                    scope.phases[2].startDate = resource.data[SIWorkflow.nick].state_data.frozen.start_date;
                }
                if (resource.data[SIWorkflow.nick].state_data.result) {
                    scope.phases[2].endDate = resource.data[SIWorkflow.nick].state_data.result.start_date;
                    scope.phases[3].startDate = resource.data[SIWorkflow.nick].state_data.result.start_date;
                }
            });

            scope.phases = [{
                name: "announce",
                title: "Information",
                description: "Ab dem Start der Ideensammlungsphase können alle interessierten Bürger*innen sich " +
                    "beteiligen und Vorschläge für Projekte in der Bezirksregion einreichen, diskutieren und " +
                    "bewerten. Am Ende der Ideensammlungsphase findet die Bürgerversammlung statt, wo Vorschläge " +
                    "vor Ort eingereicht, vorgestellt und abgestimmt werden. In der Phase „Ergebnisse“ können alle " +
                    "Interessierten die Vorschläge sehen, die realisiert werden.",
                processType: "Kiezkasse",
                votingAvailable: false,
                commentAvailable: false
            }, {
                name: "participate",
                title: "Ideensammlung",
                description: "Alle Interessierten werden aufgerufen, Vorschläge für Projekte in der Bezirksregion " +
                    "zu machen. Die Angabe der Kosten soll die Mehrwertsteuer enthalten. Vorschläge können aber " +
                    "auch noch offline in der Bürgerversammlung gemacht werden. Alle Vorschläge (offline und online) " +
                    "werden dann bei der Bürgerversammlung beschlossen.",
                processType: "Kiezkasse",
                votingAvailable: true,
                commentAvailable: true
            }, {
                name: "frozen",
                title: "Bürgerversammlung",
                description: "In dieser Phase können keine Vorschläge mehr online eingereicht, kommentiert oder " +
                    "bewertet werden. Vorschläge können aber noch offline in der Bürgerversammlung gemacht werden. Alle " +
                    "Vorschläge werden dann vor Ort vorgestellt und abgestimmt. Die Art und Weise der Abstimmung bestimmt " +
                    "die Bürgerversammlung selbst. Offline-Vorschläge werden online eingereicht.",
                processType: "Kiezkasse",
                votingAvailable: false,
                commentAvailable: false
            }, {
                name: "result",
                title: "Ergebnisse",
                description: "In der Ergebnisphase wird dargestellt, welche Vorschläge realisiert werden. Diese " +
                    "werden vom zuständigen Fachamt des Bezirksamtes, ggf. gemeinsam mit den Antragstellern, umgesetzt. " +
                    "Die Projekte müssen bis Mitte Dezember realisiert und abgerechnet werden.",
                processType: "Kiezkasse",
                votingAvailable: false,
                commentAvailable: false
            }];
        }
    };
};


export var phaseDirective = (adhConfig : AdhConfig.IService) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Phase.html",
        scope: {
            phase: "="
        }
    };
};


export var editDirective = (
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service<any>,
    adhShowError,
    adhSubmitIfValid,
    moment
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Edit.html",
        scope: {
            path: "@"
        },
        require: "^adhMovingColumn",
        link: (scope, element, attrs, column : AdhMovingColumns.MovingColumnController) => {
            var process;
            scope.data = {};
            scope.showError = adhShowError;
            adhHttp.get(scope.path).then((resource) => {
                process = resource;
                scope.data.title = process.data[SITitle.nick].title;

                scope.data.announce_description = process.data[SIWorkflow.nick].announce.description;
                scope.data.announce_start_date = moment(process.data[SIWorkflow.nick].announce.start_date).format("YYYY-MM-DD");

                scope.data.draft_description = process.data[SIWorkflow.nick].draft.description;
                scope.data.draft_start_date = moment(process.data[SIWorkflow.nick].draft.start_date).format("YYYY-MM-DD");

                scope.data.participate_description = process.data[SIWorkflow.nick].participate.description;
                scope.data.participate_start_date = moment(
                                                            process.data[SIWorkflow.nick]
                                                            .participate.start_date
                                                           ).format("YYYY-MM-DD");

                scope.data.frozen_description = process.data[SIWorkflow.nick].frozen.description;
                scope.data.frozen_start_date = moment(process.data[SIWorkflow.nick].frozen.start_date).format("YYYY-MM-DD");

                scope.data.result_description = process.data[SIWorkflow.nick].result.description;
                scope.data.result_start_date = moment(process.data[SIWorkflow.nick].result.start_date).format("YYYY-MM-DD");

                scope.data.currentWorkflowState = process.data[SIWorkflow.nick].workflow_state;
            });
            adhHttp.options(scope.path, {importOptions: false}).then((raw) => {
                // extract available transitions
                scope.data.availableWorkflowStates = AdhUtil.deepPluck(raw, [
                    "data", "PUT", "request_body", "data", SIWorkflow.nick, "workflow_state"]);
            });
            scope.submit = () => {
                return adhSubmitIfValid(scope, element, scope.kiezkassenProcessForm, () => {
                    process.data[SITitle.nick].title = scope.data.title;
                    process.data["adhocracy_core.sheets.name.IName"] = undefined;
                    process.data["adhocracy_core.sheets.image.IImageReference"] = undefined;

                    if (_.contains(scope.data.availableWorkflowStates, scope.data.workflowState)) {
                        process.data[SIWorkflow.nick] = {
                            workflow_state: scope.data.workflowState
                        };
                    } else {
                        process.data[SIWorkflow.nick] = {};
                    }

                    process.data[SIWorkflow.nick]["announce"] = {};
                    process.data[SIWorkflow.nick]["announce"].description = scope.data.announce_description;
                    process.data[SIWorkflow.nick]["announce"].start_date = scope.data.announce_start_date;

                    process.data[SIWorkflow.nick]["draft"] = {};
                    process.data[SIWorkflow.nick]["draft"].description = scope.data.draft_description;
                    process.data[SIWorkflow.nick]["draft"].start_date = scope.data.draft_start_date;

                    process.data[SIWorkflow.nick]["participate"] = {};
                    process.data[SIWorkflow.nick]["participate"].description = scope.data.participate_description;
                    process.data[SIWorkflow.nick]["participate"].start_date = scope.data.participate_start_date;

                    process.data[SIWorkflow.nick]["frozen"] = {};
                    process.data[SIWorkflow.nick]["frozen"].description = scope.data.frozen_description;
                    process.data[SIWorkflow.nick]["frozen"].start_date = scope.data.frozen_start_date;

                    process.data[SIWorkflow.nick]["result"] = {};
                    process.data[SIWorkflow.nick]["result"].description = scope.data.result_description;
                    process.data[SIWorkflow.nick]["result"].start_date = scope.data.result_start_date;

                    return adhHttp.put(process.path, process);
                });
            };
        }
    };
};


export var moduleName = "adhMeinBerlinKiezkassenProcess";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhHttp.moduleName,
            AdhMovingColumns.moduleName,
            AdhPermissions.moduleName,
            AdhTabs.moduleName,
            AdhTopLevelState.moduleName
        ])
        .directive("adhMeinBerlinKiezkassenPhase", ["adhConfig", phaseDirective])
        .directive("adhMeinBerlinKiezkassenPhaseHeader", ["adhConfig", "adhHttp", "adhTopLevelState", phaseHeaderDirective])
        .directive("adhMeinBerlinKiezkassenDetail", ["adhConfig", "adhHttp", "adhPermissions", detailDirective])
        .directive("adhMeinBerlinKiezkassenEdit", ["adhConfig", "adhHttp", "adhShowError", "adhSubmitIfValid", "moment", editDirective]);
};
