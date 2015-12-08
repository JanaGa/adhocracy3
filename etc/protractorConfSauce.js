var exec = require("sync-exec");
var fs = require("fs");
var ini = require("ini");
var pr = process.env.TRAVIS_PULL_REQUEST;
var name = ((pr === "false") ? "" : "#" + pr + " ") + process.env.TRAVIS_COMMIT;

exports.config = {
    suites: {
        current: "../src/current/current/tests/acceptance/*Spec.js",
        core: "../src/adhocracy_frontend/adhocracy_frontend/tests/acceptance/*Spec.js"
    },
    baseUrl: "http://localhost:9090",
    sauceUser: "liqd",
    sauceKey: "77600374-1617-4d7b-b1b6-9fd82ddfe89c",

    capabilities: {
        "browserName": "chrome",
        "tunnel-identifier": process.env.TRAVIS_JOB_NUMBER,
        "build": process.env.TRAVIS_BUILD_NUMBER,
        "name": name
    },
    beforeLaunch: function() {
        exec("bin/supervisord");
        exec("bin/supervisorctl restart adhocracy_test:test_zeo test_backend_with_ws adhocracy_test:test_autobahn adhocracy_test:test_frontend");
        exec("src/current/current/tests/acceptance/setup_test.sh");
    },
    afterLaunch: function() {
        exec("bin/supervisorctl stop adhocracy_test:test_zeo test_backend_with_ws adhocracy_test:test_autobahn adhocracy_test:test_frontend");
        exec("rm -rf var/test_zeodata/Data.fs* var/test_zeodata/blobs");
    },
    onPrepare: function() {
        var getMailQueuePath = function() {
            var testConf = ini.parse(fs.readFileSync("etc/test_with_ws.ini", "utf-8"));
            return testConf["app:main"]["mail.queue_path"]
                   .replace("%(here)s", process.cwd() + "/etc");
        };

        browser.params.mail = {
            queue_path: getMailQueuePath()
        }
    },
    allScriptsTimeout: 21000,
    getPageTimeout: 20000,
    jasmineNodeOpts: {
        showColors: true,
        defaultTimeoutInterval: 120000,
        isVerbose: true,
        includeStackTrace: true
    }
}
