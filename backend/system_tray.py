
import webview
import time
from api import Api

class SystemTray:
    def __init__(self, encryption_manager, entry):
        self.encryption_manager = encryption_manager
        self.entry = entry
        self.email, self.password = self.encryption_manager.load_credentials()
        self.api = Api(self.encryption_manager, self.email, self.password)
        self.window = webview.create_window("Timesheet Desktop App", self.entry, js_api=self.api, width=600, height=800)

    def logout(self, systray):
        """Logout and remove credentials."""
        self.encryption_manager.remove_credentials()
        self.email, self.password = None, None
        print("Logged out. Please provide credentials again.")
        self.show_login_prompt(systray)

    def configure(self):
        webview.start(debug=True)

    def destroy(self):
        # show the window for a few seconds before destroying it:
        time.sleep(5)
        print('Destroying window..')
        self.window.destroy()
        print('Destroyed!')