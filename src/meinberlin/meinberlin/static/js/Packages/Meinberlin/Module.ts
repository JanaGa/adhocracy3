import * as AdhMeinberlinKiezkasseModule from "./Kiezkasse/Module";
import * as AdhMeinberlinBplanModule from "./Bplan/Module";
import * as AdhMeinberlinAlexanderplatzModule from "./Alexanderplatz/Module";
import * as AdhMeinberlinBuergerhaushaltModule from "./Buergerhaushalt/Module";
import * as AdhMeinberlinPhaseModule from "./Phase/Module";
import * as AdhMeinberlinStadtforumModule from "./Stadtforum/Module";
import * as AdhMeinberlinEngagementLandschaftModule from "././DebateWorkbench/Module";

export var moduleName = "adhMeinberlin";

export var register = (angular) => {
    AdhMeinberlinKiezkasseModule.register(angular);
    AdhMeinberlinBplanModule.register(angular);
    AdhMeinberlinAlexanderplatzModule.register(angular);
    AdhMeinberlinBuergerhaushaltModule.register(angular);
    AdhMeinberlinPhaseModule.register(angular);
    AdhMeinberlinStadtforumModule.register(angular);
    AdhMeinberlinEngagementLandschaftModule.register(angular);

    angular
        .module(moduleName, [
            AdhMeinberlinAlexanderplatzModule.moduleName,
            AdhMeinberlinBplanModule.moduleName,
            AdhMeinberlinKiezkasseModule.moduleName,
            AdhMeinberlinBuergerhaushaltModule.moduleName,
            AdhMeinberlinStadtforumModule.moduleName,
            AdhMeinberlinEngagementLandschaftModule.moduleName
        ]);
};
