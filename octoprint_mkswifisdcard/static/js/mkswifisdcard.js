
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