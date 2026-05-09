# selenium_driverkit/__init__.py
import os

from selenium_driverkit.platforms.linux.chromium import get_driver_chromium as _linux_chromium
from selenium_driverkit.platforms.macos.chromium import get_driver_chromium as _macos_chromium
from selenium_driverkit.platforms.windows.chromium import get_driver_chromium as _windows_chromium

from selenium_driverkit.platforms.linux.firefox import get_driver_firefox as _linux_firefox
from selenium_driverkit.platforms.macos.firefox import get_driver_firefox as _macos_firefox
from selenium_driverkit.platforms.windows.firefox import get_driver_firefox as _windows_firefox





DEFAULT_STORAGE = os.path.join(os.path.expanduser("~"), ".selenium_driverkit")





def get_driver(browser: str, platform: str = "linux", download_path: str = None, auto_update: bool = True):
    browser = browser.lower().strip()
    platform = platform.lower().strip()

    if download_path is None:
        download_path = DEFAULT_STORAGE

    if platform == "linux":
        if browser in ("chrome", "chromium"):
            return _linux_chromium(browser=browser, download_path=download_path, auto_update=auto_update)
        elif browser == "firefox":
            return _linux_firefox(download_path=download_path, auto_update=auto_update)
        else:
            raise ValueError(f"[selenium_dk] unsupported browser: '{browser}', use 'chrome', 'chromium', 'firefox'.")

    elif platform == "windows":
        if browser in ("chrome", "chromium"):
            return _windows_chromium(browser=browser, download_path=download_path, auto_update=auto_update)
        elif browser == "firefox":
            return _windows_firefox(download_path=download_path, auto_update=auto_update)
        else:
            raise ValueError(f"[selenium_dk] unsupported browser: '{browser}', use 'chrome', 'chromium', 'firefox'.")

    elif platform == "macos":
        if browser in ("chrome", "chromium"):
            return _macos_chromium(browser=browser, download_path=download_path, auto_update=auto_update)
        elif browser == "firefox":
            return _macos_firefox(download_path=download_path, auto_update=auto_update)
        else:
            raise ValueError(f"[selenium_dk] unsupported browser: '{browser}', use 'chrome', 'chromium', 'firefox'.")
    else:
        raise ValueError(f"[selenium_dk] unknown platform: '{platform}', use 'linux', 'windows', or 'macos'.")