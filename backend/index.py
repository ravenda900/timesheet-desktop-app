import os
from time import time
from encryption import EncryptionManager
from system_tray import SystemTray
from PIL import Image
from pystray import Icon, Menu as menu, MenuItem as item


def get_entrypoint():
    def exists(path):
        return os.path.exists(os.path.join(os.path.dirname(__file__), path))

    if exists("../gui/index.html"):  # unfrozen development
        return "../gui/index.html"

    if exists("../Resources/gui/index.html"):  # frozen py2app
        return "../Resources/gui/index.html"

    if exists("./gui/index.html"):
        return "./gui/index.html"

    raise Exception("No index.html found")


def init_system_tray(entry):
    # Initialize encryption manager
    encryption_manager = EncryptionManager()

    # Initialize the tray application
    tray = SystemTray(encryption_manager, entry)

    # Set up the tray icon with a tooltip, icon path, and menu options
    try:
        tray.start_webview_process()
        tray.run_tray()
        tray.webview_process.terminate()
    except Exception as e:
        print(f"Error initializing system tray: {e}")


if __name__ == "__main__":
    entry = get_entrypoint()
    init_system_tray(entry)