/// <reference path="../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>

/**
 * cut ranges out of an array - original by John Resig (MIT Licensed)
 */
export function cutArray(a : any[], from : number, to ?: number) : any[] {
    "use strict";
    var rest = a.slice((to || from) + 1 || a.length);
    a.length = from < 0 ? a.length + from : from;
    a.push.apply(a, rest);
    return a;
};


/**
 * isArrayMember could be inlined, but is not for two reasons: (1)
 * even though js developers are used to it, the inlined idiom is just
 * weird; (2) the test suite documents what can and cannot be done
 * with it.
 */
export function isArrayMember(member : any, array : any[]) : boolean {
    "use strict";
    return array.indexOf(member) > -1;
}


/**
 * Do a deep copy on any javascript object.  The resuling object does
 * not share sub-structures as the original.  (I think instances of
 * classes other than Object, Array are not treated properly either.)
 *
 * A competing (and possibly more sophisticated) implementation is
 * available as `cloneDeep` in <a href="http://lodash.com/">lo-dash</a>
 */
export function deepcp(i) {
    "use strict";

    // base types
    if (i === null || ["number", "boolean", "string"].indexOf(typeof(i)) > -1) {
        return i;
    }

    // structured types
    var o;
    switch (Object.prototype.toString.call(i)) {
        case "[object Object]":
            o = new Object();
            break;
        case "[object Array]":
            o = new Array();
            break;
        default:
            throw "deepcp: unsupported object type!";
    }

    for (var x in i) {
        if (i.hasOwnProperty(x)) {
            o[x] = deepcp(i[x]);
        }
    }

    return o;
}


/**
 * Do a deep copy of a javascript source object into a target object.
 * References to the target object are not severed; rather, all fields
 * in the target object are deleted, and all fields in the source
 * object are copied using deepcp().  Since this function only makes
 * sense on objects, and not on other types, it crashes if either
 * argument is not an object.
 */
export function deepoverwrite(source, target) {
    "use strict";

    if (Object.prototype.toString.call(source) !== "[object Object]") {
        throw "Util.deepoverwrite: source object " + source + " not of type 'object'!";
    }
    if (Object.prototype.toString.call(target) !== "[object Object]") {
        throw "Util.deepoverwrite: target object " + target + " not of type 'object'!";
    }

    var k;
    for (k in target) {
        if (target.hasOwnProperty(k)) {
            delete target[k];
        }
    }
    for (k in source) {
        if (source.hasOwnProperty(k)) {
            target[k] = deepcp(source[k]);
        }
    }
}


/**
 * Compare two objects, and return a boolen that states whether they
 * are equal.  (This is likely to be an approximation, but it should
 * work at least for json objects.)
 */
export function deepeq(a : any, b : any) : boolean {
    "use strict";

    if (Object.prototype.toString.call(a) !== Object.prototype.toString.call(b)) {
        return false;
    }

    if (typeof(a) === "object") {
        if (a === null) {
            return (b === null);
        }

        for (var x in a) {
            if (a.hasOwnProperty(x)) {
                if (!(x in b)) {
                    return false;
                }
                if (!deepeq(a[x], b[x])) {
                    return false;
                }
            }
        }

        for (var y in b) {
            if (b.hasOwnProperty(y)) {
                if (!(y in a)) {
                    return false;
                }
            }
        }
        return true;
    } else {
        return a === b;
    }
}


/**
 * sugar for angular
 */
export function mkPromise($q : ng.IQService, obj : any) : ng.IPromise<any> {
    "use strict";

    var deferred = $q.defer();
    deferred.resolve();
    return deferred.promise.then(() => obj);
}


/**
 * Take a maximum delay time, an array of arguments and a function.
 * Generate random delays (in ms) for each and calls the function
 * asynchronously (out of order) on each element of the array.  Ignore
 * return values of f.
 *
 * Example:
 *
 * | trickle($timeout, 5000, paths, (path) => $scope.messages.push({ "event": "modified", "resource": path }));
 */
export var trickle = <T>($timeout: ng.ITimeoutService, maxdelay: number, xs: T[], f: (T) => void): void => {
    xs.map((x) => $timeout(() => f(x), Math.random() * maxdelay, true));
};


/**
 * Remove last hierarchy level from path (uris or directory paths).
 */
export function parentPath(url : string) : string {
    "use strict";

    return url.substring(0, url.lastIndexOf("/"));
};


/**
 * replace space with _, make everything lower case.
 */
export function normalizeName(name: string) : string {
    "use strict";

    return name.toLowerCase().replace(/\ /g, "_");
}

/**
 * format strings
 *
 * Example:
 *   > formatString("Hello {0} from {1}", "World", "Bernd")
 *   "Hello World from Bernd"
 *
 * http://stackoverflow.com/questions/610406/4673436#4673436
 */
export function formatString(format : string, ...args : string[]) {
    "use strict";

    return format.replace(/{(\d+)}/g, function(match, number) {
        return (typeof args[number] !== "undefined") ? args[number] : match;
    });
}


/**
 * Escape angular expression.
 *
 * This is mainly used to prevent XSS.
 *
 * If you want to use the output of this in HTML, please remember
 * to escape it using _.escape.
 */
export function escapeNgExp(s : string) {
    "use strict";
    return "'" + s.replace(/'/g, "\\'") + "'";
}
