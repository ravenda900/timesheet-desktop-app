
import webview
from api import Api
import multiprocessing
import sys
import webview
import webview.menu as wm
from PIL import Image
from pystray import Icon, Menu as menu, MenuItem as item
import os
import time

webview.settings['OPEN_DEVTOOLS_IN_DEBUG'] = False

from helpers import set_interval

if sys.platform == 'darwin':
    ctx = multiprocessing.get_context('spawn')
    Process = ctx.Process
    Queue = ctx.Queue
else:
    Process = multiprocessing.Process
    Queue = multiprocessing.Queue

class SystemTray:
    def __init__(self, encryption_manager, entry):
        self.encryption_manager = encryption_manager
        self.entry = entry
        self.api = Api(self.encryption_manager)
        self.is_logout_visible = False
        self.is_mode_visible = False
        self.main_menu_item_text = 'Login'

    def run_webview(self):
        window = webview.create_window(
            'Timesheet Desktop App', 
            self.entry, 
            js_api=self.api, 
            width=600, 
            height=800, 
            # confirm_close=True
        )
        webview.start(self.run_tasks, debug=True, ssl=True, icon='backend/assets/16x16.ico')

    def logout(self, icon, item):
        self.encryption_manager.remove_credentials()

    def run_tasks(self):
        self.api.has_credentials()
        self.api.get_projects()
        self.api.get_missing_entries()
        self.api.timesheet.scheduled_run(self.open_dialog)

    def start_webview_process(self):
        self.webview_process = Process(target=self.run_webview)
        self.webview_process.start()

    def on_open(self, icon, item):
        self.open_dialog()
            
    @set_interval(1)
    def handle_menu_item_states(self, icon):
        email, password = self.encryption_manager.load_credentials()
        has_credentials = bool(email and password)
        self.is_logout_visible = has_credentials
        self.is_mode_visible = has_credentials and os.path.exists('./config.ini') and not self.webview_process.is_alive()
        if has_credentials:
            self.main_menu_item_text = 'Configure'
        else:
            self.main_menu_item_text = 'Login'

        icon.update_menu()

    def open_dialog(self):
        if not self.webview_process.is_alive():
            self.start_webview_process()

    def set_state(self, section, option, value):
        def inner(icon, item):
            self.api.config.update_config(section, option, value)
            icon.notify(f'{option.capitalize()} has been updated')
        return inner

    def get_state(self, section, option, value):
        def inner(item):
            return self.api.config.get_config(section, option) == value
        return inner

    def run_tray(self):
        image = Image.open('backend/assets/16x16.ico')

        submenu = menu(lambda: (
            item(
                'Automatic',
                self.set_state('General', 'mode', 'Automatic'),
                checked=self.get_state('General', 'mode', 'Automatic'),
                radio=True
            ),
            item(
                'Manual',
                self.set_state('General', 'mode', 'Manual'),
                checked=self.get_state('General', 'mode', 'Manual'),
                radio=True
            )
        ))
        
        icon = Icon('Timesheet Desktop App', image, menu=menu(
            item(lambda text: self.main_menu_item_text, self.on_open, default=True),
            item('Mode', submenu, visible=lambda item: self.is_mode_visible),
            item('Logout', self.logout, visible=lambda item: self.is_logout_visible), 
            menu.SEPARATOR,
            item('Exit', lambda icon, item: icon.stop())
        ))
        self.handle_menu_item_states(icon)
        icon.run()