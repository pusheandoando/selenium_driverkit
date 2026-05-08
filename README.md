# Selenium DriverKit (selenium_driverkit)
Automated WebDriver downloader and manager for Selenium. Handles downloading, caching, and version-matching of browser drivers so you can skip the tedious manual setup.





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
driver_path = get_driver(browser="chrome", platform="windows")

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
| `browser` | `str` | required | `"chrome"`, `"chromium"`, or `"firefox"` |
| `platform` | `str` | `"linux"` | `"linux"`, `"windows"`, or `"macos"` |
| `download_path` | `str` | `None` | Custom storage path. Defaults to `~/.selenium_driverkit/` |
| `auto_update` | `bool` | `True` | Re-download driver when version mismatch is detected |

Returns the absolute path string to the driver binary, or `None` on failure.





## Storage
Drivers are stored under:
```
~/.selenium_driverkit/
    Drivers/
        Chromium/
            Linux/
            Windows/
            MacOS/
        Firefox/
            Linux/
            Windows/
            MacOS/
```