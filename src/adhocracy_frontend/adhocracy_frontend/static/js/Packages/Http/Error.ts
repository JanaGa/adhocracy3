/// <reference path="../../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>

// Error responses in the Adhocracy REST API contain json objects in
// the body that have the following form:
export interface IBackendError {
    status: string;
    errors: IBackendErrorItem[];
}

export interface IBackendErrorItem {
    name : string;
    location : string;
    description : string;
}

var renderBackendError = (response : ng.IHttpPromiseCallbackArg<any>) : void => {
    // get rid of unrenderable junk (good for console log extraction with web driver).
    var sanitize = (x : any) : any => {
        if (typeof x === "undefined") {
            return x;
        } else {
            return JSON.parse(JSON.stringify(x));
        }
    };

    console.log("http response with error status: " + response.status);
    console.log("request:", sanitize(response.config));
    console.log("headers:", sanitize(response.headers));
    console.log("response:", sanitize(response.data));
};

export var logBackendError = (response : ng.IHttpPromiseCallbackArg<IBackendError>) : void => {
    "use strict";

    renderBackendError(response);

    var errors : IBackendErrorItem[] = response.data.errors;
    throw errors;
};

/**
 * batch requests recive an array of responses.  each response matches
 * one request that was actually processed in the backend.  Since the
 * first error makes batch processing stop, all responses up to the
 * last one are successes.  If this function is called, the error is
 * contained in the last element of the array.  All other elements are
 * ignored by this function.
 *
 * NOTE: See documentation of `importBatchContent`.
 */
export var logBackendBatchError = (
    response : ng.IHttpPromiseCallbackArg<{
        code : number;
        body : IBackendError;
    }[]>
) : void => {
    "use strict";

    renderBackendError(response);

    var lastBatchItemResponse : IBackendError = response.data[response.data.length - 1].body;
    var errors : IBackendErrorItem[] = lastBatchItemResponse.errors;
    throw errors;
};
