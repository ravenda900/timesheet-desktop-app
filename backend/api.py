import os
import webview
from config import Config
from timesheet import Timesheet

class Api:
    def __init__(self, encryption_manager, email, password):
        self.encryption_manager = encryption_manager
        self.email, self.password = self.encryption_manager.load_credentials()
        self.config = Config()
        self.timesheet = Timesheet(email, password, self)

    def fullscreen(self):
        webview.windows[0].toggle_fullscreen()

    def save_content(self, content):
        filename = webview.windows[0].create_file_dialog(webview.SAVE_DIALOG)
        if not filename:
            return

        with open(filename, "w") as f:
            f.write(content)

    def ls(self):
        return os.listdir(".")
    
    def has_credentials(self):
        return self.email and self.password
    
    def store_credentials(self, email, password):
        self.encryption_manager.store_credentials(email, password)

    def store_configuration(self, config):
        self.config.create_config(config['mode'], config['scheduledTime'], config['time'], config['endNextDay'], config['breakTime'], config['comment'], config['project'])

    def has_configuration(self):
        return os.path.exists('./config.ini')

    def get_configuration(self, is_api):
        return self.config.read_config(is_api)

    def get_projects(self):
        return self.timesheet.projects
