# coding=utf-8

import io
import logging
import os
import threading
import time

import requests

import octoprint.plugin
from octoprint.events import Events, eventManager


class mkswifisdcardPlugin(
    octoprint.plugin.StartupPlugin,
    octoprint.plugin.AssetPlugin,
    octoprint.plugin.TemplatePlugin,
    octoprint.plugin.SettingsPlugin
):
    def on_after_startup(self):
        self._logger.info("MKS WiFi host: %s" % self._settings.get(["host"]))

    def custom_upload_to_sd(
        self,
        printer,
        filename,
        path,
        sd_upload_started,
        sd_upload_succeeded,
        sd_upload_failed,
        *args,
        **kwargs
    ):

        remote_name = printer._get_free_remote_name(filename)
        self._logger.info(
            "Starting SDCard upload from {} {} to {}".format(path, filename, remote_name)
        )

        sd_upload_started(filename, remote_name)
        start_time = time.time()

        def change_state_handler(event, data):
            if data["state_id"] == "OPERATIONAL":
                sd_upload_succeeded(filename, remote_name, time.time() - start_time)
                eventManager().unsubscribe(
                    Events.PRINTER_STATE_CHANGED, change_state_handler
                )

        def set_upload_progress(progress):
            self._plugin_manager.send_plugin_message(
                "mkswifisdcard", dict(progress=int(progress))
            )
        
        def run_upload():
            set_upload_progress(0)
            printer.disconnect()
            self.upload_via_wifi(path, remote_name, self._settings.get(["host"]), set_upload_progress)
            set_upload_progress(100)
            printer.connect()
            
        eventManager().subscribe(Events.PRINTER_STATE_CHANGED, change_state_handler)
        run_upload()
        #thread = threading.Thread(target = run_upload)
        #thread.daemon = True
        #thread.start()      

        return remote_name

    def upload_via_wifi(self, path, filename, host, callback):        
        res = requests.post(
            url="http://%s/upload?X-Filename=%s" % (host, filename),
            data=ProgressUpload(path, callback),
            headers={
                "Content-Type": "application/octet-stream",
                "Connection": "keep-alive",
            },
        )
        
    
    # TemplatePlugin mixin
    def get_template_configs(self):
        return [{"type": "settings", "custom_bindings": False}]
    
    # SettingsPlugin mixin
    def get_settings_defaults(self):
        return dict(host="")

    # AssetPlugin mixin
    def get_assets(self):
        # Define your plugin's asset files to automatically include in the
        # core UI here.
        return {"js": ["js/mkswifisdcard.js"]}


class ProgressUpload:
    def __init__(self, filename, callback, chunk_size=1048576):
        self.filename = filename
        self.chunk_size = chunk_size
        self.callback = callback
        self.file_size = os.path.getsize(filename)
        self.size_read = 0

    def __iter__(self):
        with open(self.filename, "rb") as f:
            for chunk in iter(lambda: f.read(self.chunk_size), b""):
                self.size_read += len(chunk)
                yield chunk
                self.callback((int)(self.size_read / self.file_size * 100))

    def __len__(self):
        return self.file_size


# Set the Python version your plugin is compatible with below. Recommended is Python 3 only for all new plugins.
# OctoPrint 1.8.0 onwards only supports Python 3.
__plugin_pythoncompat__ = ">=3,<4"  # Only Python 3


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = mkswifisdcardPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.printer.sdcardupload": __plugin_implementation__.custom_upload_to_sd
    }
