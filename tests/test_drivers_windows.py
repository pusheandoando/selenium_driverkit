# tests/test_drivers_windows.py
from selenium_driverkit import get_driver





BROWSERS = [
    "chrome",
    "chromium",
    "firefox"
]





if __name__ == '__main__':
    for browser in BROWSERS:
        try:
            driver_path = get_driver(
                browser = browser,
                platform = "windows",
                auto_update = True
            )

            print("\n")
            print(f"{browser.capitalize()} driver path: {driver_path}")
        except Exception as error_log:
            print("[TEST Error]")
            print(error_log)