import _ = require("lodash");

import AdhConfig = require("../Config/Config");
import AdhTopLevelState = require("../TopLevelState/TopLevelState");
import AdhUtil = require("../Util/Util");

var pkgLocation = "/Embed";


var metaParams = [
    "autoresize",
    "initialUrl",
    "locale",
    "nocenter",
    "noheader"
];

export class Provider {
    public embeddableDirectives : string[];
    public contexts : string[];
    public $get;

    /**
     * List of directive names that can be embedded.  names must be in
     * lower-case with dashes, but without 'adh-' prefix.  (example:
     * 'document-workbench' for directive DocumentWorkbench.)
     */
    constructor() {
        this.embeddableDirectives = [
            "document-workbench",
            "paragraph-version-detail",
            "comment-listing",
            "create-or-show-comment-listing",
            "login",
            "register",
            "user-indicator",
            "empty"
        ];

        this.contexts = [
            "plain"
        ];

        this.$get = ["adhConfig", (adhConfig) => new Service(this, adhConfig)];
    }

    public registerEmbeddableDirectives(directives : string[]) : void {
        for (var i = 0; i < directives.length; i++) {
            var directive = directives[i];
            // remove <any> when borisyankov/DefinitelyTyped#3573 is resolved
            if (!(<any>_).includes(this.embeddableDirectives, directive)) {
                this.embeddableDirectives.push(directive);
            }
        }
    }

    public registerContext(name : string) : void {
        this.contexts.push(name);
    }
}

export class Service {
    private widget : string;

    constructor(
        protected provider : Provider,
        protected adhConfig : AdhConfig.IService
    ) {/* pass */}

    private location2template(widget : string, search) {
        var attrs = [];

        if (widget === "empty") {
            return "";
        }
        for (var key in search) {
            if (search.hasOwnProperty(key) && metaParams.indexOf(key) === -1) {
                attrs.push(AdhUtil.formatString("data-{0}=\"{1}\"", _.escape(key), _.escape(search[key])));
            }
        }
        return AdhUtil.formatString("<adh-{0} {1}></adh-{0}>", _.escape(widget), attrs.join(" "));
    }

    public isEmbedded() : boolean {
        return typeof this.widget !== "undefined";
    }

    public getContext() : string {
        if (!this.isEmbedded() || this.widget === "plain") {
            return "";
        } else {
            return this.widget;
        }
    }

    public route($location : angular.ILocationService) : AdhTopLevelState.IAreaInput {
        var widget : string = $location.path().split("/")[2];
        var search = $location.search();

        // For later use
        this.widget = widget;

        // FIXME: DefinitelyTyped: remove <any> when borisyankov/DefinitelyTyped#3573 is resolved
        if ((<any>_).includes(this.provider.embeddableDirectives, widget)) {
            var template = this.location2template(widget, search);

            if (!search.hasOwnProperty("nocenter")) {
                template = "<div class=\"l-center m-embed\">" + template + "</div>";
            }

            if (!search.hasOwnProperty("noheader")) {
                var headerTemplateUrl = this.adhConfig.pkg_path + pkgLocation + "/Header.html";
                template = "<ng-include src=\"'" + headerTemplateUrl + "'\"></ng-include>" + template;
            }

            return {
                template: template
            };
        } else if ((<any>_).includes(this.provider.contexts, widget)) {
            $location.url(search.initialUrl || "/");
            $location.replace();

            return {
                skip: true
            };
        } else {
            throw "unknown widget: " + widget;
        }
    }
}


export var normalizeInternalUrl = (url : string, $location : angular.ILocationService) => {
    var host = $location.protocol() + "://" + $location.host();
    var port = $location.port();
    if (port && (port !== 80) && (port !== 443)) {
        host = host + ":" + port;
    }
    if (url.lastIndexOf(host, 0) === 0) {
        url = url.substring(host.length);
    }
    return url;
};


export var isInternalUrl = (url : string, $location : angular.ILocationService) => {
    return normalizeInternalUrl(url, $location)[0] === "/";
};


export var hrefDirective = (adhConfig : AdhConfig.IService, $location, $rootScope) => {
    return {
        restrict: "A",
        link: (scope, element, attrs) => {
            if (element[0].nodeName === "A") {
                scope.$watch(() => attrs.href, (orig) => {
                    // remove any handlers that were registered in previous runs
                    element.off("click.adh_href");

                    if (orig && orig[0] !== "#") {
                        orig = normalizeInternalUrl(orig, $location);

                        if (isInternalUrl(orig, $location)) {
                            // set href to canonical url while preserving click behavior
                            element.attr("href", adhConfig.canonical_url + orig);
                            element.on("click.adh_href", (event) => {
                                if (event.button === 0) {
                                    _.defer(() => $rootScope.$apply(() => {
                                        $location.url(orig);
                                    }));
                                    event.preventDefault();
                                }
                            });
                        }
                    }
                });
            }
        }
    };
};

export var canonicalUrl = (adhConfig : AdhConfig.IService) => {
    return (internalUrl : string) : string => {
        return adhConfig.canonical_url + internalUrl;
    };
};
