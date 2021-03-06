import * as AdhEmbedModule from "../../../Embed/Module";
import * as AdhResourceAreaModule from "../../../ResourceArea/Module";

import * as AdhEuthWorkbenchModule from "../Workbench/Module";

import * as AdhEmbed from "../../../Embed/Embed";

import * as AdhEuthWorkbench from "../Workbench/Workbench";

import RIEuthProcess from "../../../../Resources_/adhocracy_euth/resources/idea_collection/IProcess";
import RIEuthPrivateProcess from "../../../../Resources_/adhocracy_euth/resources/idea_collection/IPrivateProcess";


export var moduleName = "adhPcompassContext";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhEmbedModule.moduleName,
            AdhEuthWorkbenchModule.moduleName,
            AdhResourceAreaModule.moduleName,
        ])
        .config(["adhEmbedProvider", (adhEmbedProvider : AdhEmbed.Provider) => {
            adhEmbedProvider.registerContext("euth");
        }])
        .config(["adhResourceAreaProvider", AdhEuthWorkbench.registerRoutes(RIEuthProcess, "euth")])
        .config(["adhResourceAreaProvider", AdhEuthWorkbench.registerRoutes(RIEuthPrivateProcess, "euth")]);
};
