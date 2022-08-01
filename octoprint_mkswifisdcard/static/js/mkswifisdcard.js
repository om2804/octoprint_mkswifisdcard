
$(function () {
    function mkswifisdcardViewModel(parameters) {
        var self = this;

        // assign the injected parameters, e.g.:
        self.filesViewModel = parameters[0];

        self.onDataUpdaterPluginMessage = function (plugin, data) {

            if (plugin != "mkswifisdcard") {
                return;
            }

            if (data.hasOwnProperty("progress")) {
                self.filesViewModel._setProgressBar(data["progress"], 'Uploading to sd - ' + data["progress"] + '%...', false);
            }

            if (data.hasOwnProperty("error")) {
                new PNotify({
                    title: 'MKS WiFi SD-card Error',
                    text: '<div class="row-fluid"><p>Error of uploading to sd-card over WiFi. Check your settings.</p><p><pre style="padding-top: 5px;">'+data["error"]+'</pre></p>',
                    hide: true
                });
                return;
            }
        }
    }

    /* view model class, parameters for constructor, container to bind to
     * Please see http://docs.octoprint.org/en/master/plugins/viewmodels.html#registering-custom-viewmodels for more details
     * and a full list of the available options.
     */
    OCTOPRINT_VIEWMODELS.push({
        construct: mkswifisdcardViewModel,
        dependencies: ["filesViewModel"]
    });
});