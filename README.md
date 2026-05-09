# Selenium DriverKit (selenium_driverkit)
Automated WebDriver downloader and manager for Selenium. Handles downloading, caching, and version-matching of browser drivers so you can skip the tedious manual setup.





## Supported Browsers
| Browser | | Status |
|---|---|---|
| <img src="assets/icon_chrome.svg" width="28" height="28"> | Google Chrome | Supported |
| <img src="assets/icon_chromium.svg" width="28" height="28"> | Chromium | Supported |
| <img src="assets/icon_firefox.svg" width="28" height="28"> | Firefox | Supported |





## Supported Platforms
| Platform | | Status |
|---|---|---|
| <img src="assets/os_icon_linux.svg" width="28" height="28"> | Linux | Supported |
| <img src="assets/os_icon_windows.svg" width="28" height="28"> | Windows | Supported |
| <img src="assets/os_icon_macos.svg" width="28" height="28"> | MacOS | Supported |





## Installation
```bash
pip3 install --upgrade git+https://github.com/pusheandoando/selenium_driverkit.git
```





## Usage
```python
from selenium_driverkit import get_driver

# Chrome / Chromium
driver_path = get_driver(browser="chrome", platform="linux")

# Firefox
driver_path = get_driver(browser="firefox", platform="linux")

# Windows
driver_path = get_driver(browser="chromium", platform="windows")

# MacOS
driver_path = get_driver(browser="firefox", platform="macos")

# Custom download path
driver_path = get_driver(
    browser = "chrome",
    platform = "linux",
    download_path = "/custom/path",
    auto_update = True
)
```





### Parameters
| Parameter | Type | Default | Description |
|---|---|---|---|
| `browser` | `str` | required | `"chrome"`, `"chromium"`, `"firefox"` |
| `platform` | `str` | `"linux"` | `"linux"`, `"windows"`, `"macos"` |
| `download_path` | `str` | `None` | Custom storage path |
| `auto_update` | `bool` | `True` | Re-download driver when version mismatch is detected |

Returns the absolute path string to the driver binary, or `None` on failure.





## Storage
Drivers are stored under:
```
~/.selenium_driverkit/
    Drivers/
        Chromium/
            Linux/
                Chrome/
                Chromium/
            Windows/
                Chrome/
                Chromium/
            MacOS/
                Chrome/
                Chromium/
        Firefox/
            Linux/
            Windows/
            MacOS/
```