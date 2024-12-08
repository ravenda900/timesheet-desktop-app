import os
import webview
from helpers import set_interval
from config import Config
from timesheet import Timesheet
import json

class Api:
    def __init__(self, encryption_manager):
        self.encryption_manager = encryption_manager
        self.timesheet = Timesheet(encryption_manager, self)
        self.config = Config()
    
    @set_interval(1)
    def has_credentials(self):
        if len(webview.windows) > 0:
            email, password = self.encryption_manager.load_credentials()
            has_credentials = bool(email and password)
            webview.windows[0].evaluate_js(
                f'window.pywebview.state && window.pywebview.state.setHasCredentials && window.pywebview.state.setHasCredentials({'true' if has_credentials else 'false'})'
            )
    
    def store_credentials(self, email, password):
        self.encryption_manager.store_credentials(email, password)

    def store_configuration(self, config):
        self.config.create_config(config['mode'], config['scheduledTime'], config['time'], config['endNextDay'], config['breakTime'], config['comment'], config['project'])

    def has_configuration(self):
        return os.path.exists('./config.ini')

    def get_configuration(self, is_api):
        return self.config.read_config(is_api)
    
    def create_timesheet(self):
        self.timesheet.create_timesheet()

    def create_missing_entries(self):
        if hasattr(self.timesheet, 'missing_entries'):
            for missing_entry in self.timesheet.missing_entries:
                self.timesheet.create_timesheet_entry(missing_entry)

    def create_missing_entry(self, date):
        self.timesheet.create_timesheet_entry(date)

    @set_interval(1)
    def get_projects(self):
        if len(webview.windows) > 0 and hasattr(self.timesheet, 'projects'):
            webview.windows[0].evaluate_js(
                'window.pywebview.state && window.pywebview.state.setProjectIssueOptions && window.pywebview.state.setProjectIssueOptions(%s)' % json.dumps(self.timesheet.projects)
            )
    
    def get_myself(self, email, password):
        return self.timesheet.get_myself(email, password)
    
    @set_interval(1)
    def get_missing_entries(self):
        if len(webview.windows) > 0 and hasattr(self.timesheet, 'missing_entries'):
            webview.windows[0].evaluate_js(
                'window.pywebview.state && window.pywebview.state.setMissingEntries && window.pywebview.state.setMissingEntries(%s)' % json.dumps(self.timesheet.missing_entries)
            )
