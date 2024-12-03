import os
import threading
from time import time
import webview
from encryption import EncryptionManager
from system_tray import SystemTray
from infi.systray import SysTrayIcon


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


# def set_interval(interval):
#     def decorator(function):
#         def wrapper(*args, **kwargs):
#             stopped = threading.Event()

#             def loop():  # executed in another thread
#                 while not stopped.wait(interval):  # until stopped
#                     function(*args, **kwargs)

#             t = threading.Thread(target=loop)
#             t.daemon = True  # stop if the program exits
#             t.start()
#             return stopped

#         return wrapper

#     return decorator


# entry = get_entrypoint()


# @set_interval(1)
# def update_ticker():
#     if len(webview.windows) > 0:
#         webview.windows[0].evaluate_js(
#             'window.pywebview.state.setTicker("%d")' % time()
#         )


def init_system_tray(entry):
    # Initialize encryption manager
    encryption_manager = EncryptionManager()

    # Initialize the tray application
    tray = SystemTray(encryption_manager, entry)

    # Check if credentials are stored, show prompt or config dialog accordingly
    # if tray.email and tray.password:
    #     tray.enqueue_show_config_dialog(None)  # Show config dialog if credentials are found
    # else:
    #     tray.show_login_prompt(None)  # Show login prompt if no credentials are stored

    # Create a SysTrayIcon with menu options
    # menu_options = (
    #     ("Configure", None, tray.configure),
    #     ("Logout", None, tray.logout),
    # )

    # Set up the tray icon with a tooltip, icon path, and menu options
    try:
        # systray = SysTrayIcon(
        #     "backend/assets/16x16.ico",  # Path to a .ico file for the tray icon
        #     "Timesheet Desktop App",  # Tooltip text
        #     menu_options,
        #     on_quit=tray.destroy,
        #     default_menu_index=0,  # Make "Configure" the default action on left-click
        # )
        # systray.start()
        scheduled_run = threading.Thread(target=tray.api.timesheet.scheduled_run)

        scheduled_run.start()
        tray.configure()
        return 
    except Exception as e:
        print(f"Error initializing system tray: {e}")


if __name__ == "__main__":
    entry = get_entrypoint()
    init_system_tray(entry)