# selenium_driverkit/platforms/macos/firefox.py
import os
import re
import tarfile
import requests
import subprocess
from tqdm import tqdm
import platform as _platform





_GECKODRIVER_RELEASES_API = "https://api.github.com/repos/mozilla/geckodriver/releases/latest"

_ARCH_MAP = {
    "x86_64": "macos",
    "arm64": "macos-aarch64",
}

_FIREFOX_APP_PATHS = [
    "/Applications/Firefox.app/Contents/MacOS/firefox",
    "/Applications/Firefox Developer Edition.app/Contents/MacOS/firefox",
    "/Applications/Firefox Nightly.app/Contents/MacOS/firefox",
]





def _get_browser_version():
    for app in _FIREFOX_APP_PATHS:
        if os.path.exists(app):
            try:
                out = subprocess.check_output([app, "--version"], stderr=subprocess.DEVNULL)
                text = out.decode("utf-8").strip()
                match = re.search(r"(\d+\.\d+(?:\.\d+)?)", text)
                if match:
                    return match.group(1)
            except (subprocess.CalledProcessError, FileNotFoundError, OSError):
                continue

    for cmd in ("firefox", "firefox-esr"):
        try:
            out = subprocess.check_output([cmd, "--version"], stderr=subprocess.DEVNULL)
            text = out.decode("utf-8").strip()
            match = re.search(r"(\d+\.\d+(?:\.\d+)?)", text)
            if match:
                return match.group(1)
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue

    raise RuntimeError(
        "[selenium_dk] could not detect Firefox version, make sure it is installed."
    )


def _get_geckodriver_version(binary_path):
    try:
        out = subprocess.check_output([binary_path, "--version"], stderr=subprocess.DEVNULL)
        text = out.decode("utf-8").strip()
        match = re.search(r"geckodriver\s+(\d+\.\d+\.\d+)", text)

        if match:
            return match.group(1)
        return None
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def _resolve_arch_suffix():
    machine = _platform.machine()
    suffix = _ARCH_MAP.get(machine)
    if not suffix:
        raise RuntimeError(f"[selenium_dk] unsupported architecture: {machine}.")
    return suffix


def _resolve_download_url(arch_suffix):
    response = requests.get(_GECKODRIVER_RELEASES_API, timeout=15)
    response.raise_for_status()
    data = response.json()

    version = data["tag_name"].lstrip("v")

    for asset in data["assets"]:
        name = asset["name"]
        if arch_suffix in name and name.endswith(".tar.gz") and ".asc" not in name:
            return version, asset["browser_download_url"]

    raise RuntimeError(
        f"[selenium_dk] no geckodriver release found for architecture suffix '{arch_suffix}'."
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


def get_driver_firefox(download_path: str, auto_update: bool = True):
    drivers_root = os.path.join(download_path, "Drivers", "Firefox", "MacOS")
    os.makedirs(drivers_root, exist_ok=True)

    binary_path = os.path.join(drivers_root, "geckodriver")

    print('\n')
    print("[ Firefox WebDriver (MacOS) ]")

    try:
        browser_version = _get_browser_version()
        print(f" - Browser version detected: {browser_version}")
    except RuntimeError as e:
        print(f" [!!] {e}")
        return None

    try:
        arch_suffix = _resolve_arch_suffix()
        print(f" - Architecture: {_platform.machine()} ({arch_suffix})")
    except RuntimeError as e:
        print(f" [!!] {e}")
        return None

    if os.path.exists(binary_path):
        installed_version = _get_geckodriver_version(binary_path)

        if installed_version:
            response = requests.get(_GECKODRIVER_RELEASES_API, timeout=15)
            response.raise_for_status()
            latest_version = response.json()["tag_name"].lstrip("v")

            if installed_version == latest_version:
                print(f" - Geckodriver already installed (version {installed_version}), nothing to do.")
                return binary_path

            print('\n')
            print(f"( Version mismatch detected )")
            print(f" - Firefox version:         {browser_version}")
            print(f" - Installed geckodriver:   {installed_version}")
            print(f" - Latest geckodriver:      {latest_version}")

            if not auto_update:
                print(" - auto_update=False, skipping update. Returning existing driver.")
                return binary_path

            print(" - Removing outdated driver...")
            os.remove(binary_path)

        else:
            print(" [!!] Could not verify existing driver version. Reinstalling...")
            os.remove(binary_path)

    try:
        print(" - Fetching latest geckodriver release...")
        driver_version, download_url = _resolve_download_url(arch_suffix)
        print(f" - Latest version: {driver_version}")
    except (RuntimeError, requests.RequestException) as e:
        print(f" [!!] {e}")
        return None

    tar_path = os.path.join(drivers_root, "geckodriver.tar.gz")

    try:
        print(f" - Downloading from: {download_url}")
        _download_file(download_url, tar_path)
    except requests.RequestException as e:
        print(f" [!!] Download failed: {e}")
        return None

    print(" - Extracting...")
    with tarfile.open(tar_path, "r:gz") as t:
        t.extractall(drivers_root)

    os.remove(tar_path)
    os.chmod(binary_path, 0o755)

    print(f" - Geckodriver installed at: {binary_path}")
    return binary_path