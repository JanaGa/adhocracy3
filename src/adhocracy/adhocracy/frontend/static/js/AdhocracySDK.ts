"use strict";

// FIXME: internal object for testing

(function() {
    var adhocracy : any = {};

    // setup window.adhocracy and noConflict()
    var _adhocracy = (<any>window).adhocracy;
    (<any>window).adhocracy = adhocracy;

    adhocracy.noConflict = () => {
        if ((<any>window).adhocracy === adhocracy) {
            (<any>window).adhocracy = _adhocracy;
        }
        return adhocracy;
    };

    var $;
    var origin : string;
    var appUrl : string = "/frontend_static/root.html";
    var embedderOrigin : string;

    /**
     * Load external JavaScript asynchronously.
     */
    var loadScript = (url: string, callback: () => void) => {
        var script = document.createElement("script");
        script.async = true;
        script.src = url;

        var entry = document.getElementsByTagName("script")[0];
        entry.parentNode.insertBefore(script, entry);

        script.onload = script.onreadystatechange = () => {
            var rdyState = script.readyState;
            if (!rdyState || /complete|loaded/.test(script.readyState)) {
                callback();
                script.onload = null;
                script.onreadystatechange = null;
            }
        };
    };

    var getIFrameByWindow = (win: Window) => {
        var result;
        $("iframe.adhocracy-embed").each((i, iframe) => {
            if (iframe.contentWindow === win) {
                result = iframe;
                return;
            }
        });
        return result;
    };

    /**
     * Handle a message that was sent by another window.
     */
    var handleMessage = (name: string, data, source: Window) : void => {
        switch (name) {
            case "resize":
                var iframe = getIFrameByWindow(source);
                $(iframe).height(data.height);
                break;
        }
    };

    /**
     * Initialize adhocracy SDK.  Must be called before using any other methods.
     *
     * @param o Origin (e.g. https://adhocracy.de)
     */
    adhocracy.init = (o: string, callback) => {
        origin = o;
        embedderOrigin = window.location.protocol + "//" + window.location.host;

        loadScript(origin + "/frontend_static/lib/jquery/jquery.js", () => {
            $ = (<any>window).jQuery.noConflict(true);

            $(window).on("message", (event) => {
                var message = JSON.parse(event.originalEvent.data);
                handleMessage(message.name, message.data, event.originalEvent.source);
            });

            callback(adhocracy);
        });
    };

    /**
     * Embed adhocracy.
     *
     * Any needed data is read from the marker.
     *
     * @param selector Selector for the markers that will be replaced by adhocracy.
     */
    adhocracy.embed = (selector: string) => {
        $(selector).each((i, e) => {
            // In the future, marker may have additional attributes or
            // child elements that have influence on iframe.
            var marker = $(e);
            var iframe = $("<iframe>");

            iframe.css("border", "none");
            iframe.css("width", "100%");
            iframe.attr("src", origin + appUrl);
            iframe.addClass("adhocracy-embed");

            marker.append(iframe);
        });
    };

    /**
     * Send a message to another window.
     *
     * @param uid ID of the target window
     * @param name Message name
     * @param data Message data
     *
     * This is redundantly implemented in
     * "Adhocracy/Services/CrossWindowMessaging".  if they start
     * growing in parallel, we should factor them out into a shared
     * module.
     */
    adhocracy.postMessage = (win: Window, name: string, data: {}) => {
        var message = {
            name: name,
            data: data
        };
        var messageString = JSON.stringify(message);

        // FIXME: use fallbacks here
        win.postMessage(messageString, origin);
    };
})();
