# selenium_driverkit/platforms/linux/chromium.py
import os
import re
import shutil
import zipfile
import requests
import subprocess
from tqdm import tqdm





_CFT_LATEST_GOOD = "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json"
_CFT_PATCH_LOOKUP = "https://googlechromelabs.github.io/chrome-for-testing/latest-patch-versions-per-build-with-downloads.json"

_ARCH_MAP = {
    "x86_64": "linux64",
    "aarch64": "linux-arm64",
    "arm64": "linux-arm64",
}

_CHROME_CANDIDATES = ["google-chrome", "google-chrome-stable"]
_CHROMIUM_CANDIDATES = ["chromium", "chromium-browser"]





def _resolve_linux_platform():
    machine = os.uname().machine
    platform_suffix = _ARCH_MAP.get(machine)
    if not platform_suffix:
        raise RuntimeError(f"[selenium_dk] unsupported architecture: {machine}.")
    return platform_suffix


def _get_chrome_version():
    for cmd in _CHROME_CANDIDATES:
        try:
            out = subprocess.check_output([cmd, "--version"], stderr=subprocess.DEVNULL)
            text = out.decode("utf-8").strip()
            match = re.search(r"(\d+\.\d+\.\d+\.\d+)", text)
            if match:
                return match.group(1)
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    raise RuntimeError("[selenium_dk] could not detect Google Chrome version, make sure it is installed.")


def _get_chromium_version():
    for cmd in _CHROMIUM_CANDIDATES:
        try:
            out = subprocess.check_output([cmd, "--version"], stderr=subprocess.DEVNULL)
            text = out.decode("utf-8").strip()
            match = re.search(r"(\d+\.\d+\.\d+\.\d+)", text)
            if match:
                return match.group(1)
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    raise RuntimeError("[selenium_dk] could not detect Chromium version, make sure it is installed.")


def _get_chromedriver_version(binary_path):
    try:
        out = subprocess.check_output([binary_path, "--version"], stderr=subprocess.DEVNULL)
        text = out.decode("utf-8").strip()
        match = re.search(r"(\d+\.\d+\.\d+\.\d+)", text)
        if match:
            return match.group(1)
        return None
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def _resolve_download_url(browser_version, platform_suffix):
    build = ".".join(browser_version.split(".")[:3])
    major = browser_version.split(".")[0]

    response = requests.get(_CFT_PATCH_LOOKUP, timeout=15)
    response.raise_for_status()
    data = response.json()
    builds = data.get("builds", {})

    build_entry = builds.get(build)
    if build_entry:
        for entry in build_entry.get("downloads", {}).get("chromedriver", []):
            if entry.get("platform") == platform_suffix:
                return build_entry["version"], entry["url"]

    response2 = requests.get(_CFT_LATEST_GOOD, timeout=15)
    response2.raise_for_status()
    data2 = response2.json()
    channels = data2.get("channels", {})

    for channel in ("Stable", "Beta", "Dev", "Canary"):
        ch = channels.get(channel, {})
        if ch.get("version", "").split(".")[0] == major:
            for entry in ch.get("downloads", {}).get("chromedriver", []):
                if entry.get("platform") == platform_suffix:
                    return ch["version"], entry["url"]

    raise RuntimeError(
        f"[selenium_dk] no chromedriver found for Chrome/Chromium {browser_version} ({platform_suffix})."
    )


def _download_file(url, dest_path):
    response = requests.get(url, stream=True, timeout=30)
    response.raise_for_status()

    total = int(response.headers.get("content-length", 0))
    bar = tqdm(total=total, unit="iB", unit_scale=True, desc="Download progress")

    with open(dest_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                bar.update(f.write(chunk))
    bar.close()


def get_driver_chromium(browser: str, download_path: str, auto_update: bool = True):
    browser_label = "Chrome" if browser == "chrome" else "Chromium"
    drivers_root = os.path.join(download_path, "Drivers", "Chromium", "Linux", browser_label)
    os.makedirs(drivers_root, exist_ok=True)

    print('\n')
    print(f"[ {browser_label} WebDriver (Linux) ]")

    try:
        if browser == "chrome":
            browser_version = _get_chrome_version()
        else:
            browser_version = _get_chromium_version()
        print(f" - Browser version detected: {browser_version}")
    except RuntimeError as e:
        print(f" [!!] {e}")
        return None

    try:
        platform_suffix = _resolve_linux_platform()
        print(f" - Architecture: {os.uname().machine} ({platform_suffix})")
    except RuntimeError as e:
        print(f" [!!] {e}")
        return None

    binary_dir = os.path.join(drivers_root, f"chromedriver-{platform_suffix}")
    binary_path = os.path.join(binary_dir, "chromedriver")
    browser_major = browser_version.split(".")[0]

    if os.path.exists(binary_path):
        installed_version = _get_chromedriver_version(binary_path)

        if installed_version:
            installed_major = installed_version.split(".")[0]

            if installed_major == browser_major:
                print(f" - Chromedriver already installed (version {installed_version}), nothing to do.")
                return binary_path

            print('\n')
            print(f"( Version mismatch detected )")
            print(f" - Browser version:     {browser_version}")
            print(f" - Installed driver:    {installed_version}")

            if not auto_update:
                print(" - auto_update=False, skipping update, returning existing driver.")
                return binary_path

            print(" - Removing outdated driver...")
            shutil.rmtree(binary_dir, ignore_errors=True)

        else:
            print(" [!!] Could not verify existing driver version, reinstalling...")
            shutil.rmtree(binary_dir, ignore_errors=True)

    try:
        print(" - Resolving matching ChromeDriver version...")
        driver_version, download_url = _resolve_download_url(browser_version, platform_suffix)
        print(f" - Resolved driver version: {driver_version}")
    except RuntimeError as e:
        print(f" [!!] {e}")
        return None

    zip_path = os.path.join(drivers_root, "chromedriver.zip")

    try:
        print(f" - Downloading from: {download_url}")
        _download_file(download_url, zip_path)
    except requests.RequestException as e:
        print(f" [!!] Download failed: {e}")
        return None

    print(" - Extracting...")
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(drivers_root)

    os.remove(zip_path)
    os.chmod(binary_path, 0o755)

    print(f" - Chromedriver installed at: {binary_path}")
    return binary_path