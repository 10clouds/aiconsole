import logging
import os
import platform
import tarfile
import urllib.request

_log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def download_python(python_version, date_tag):
    _log.info("Detecting machine architecture...")
    arch_name = platform.machine()
    system_name = platform.system()

    if system_name == "Darwin":
        if arch_name == "x86_64":
            _log.info("Detected Intel architecture for macOS.")
            variant = "x86_64-apple-darwin"
        elif arch_name == "arm64":
            _log.info("Detected Apple M1 architecture.")
            variant = "aarch64-apple-darwin"
        else:
            _log.error(f"Unknown architecture: {arch_name}")
            return False

    elif system_name == "Linux":
        _log.info("Detected Linux architecture.")
        variant = "x86_64-unknown-linux-gnu"

    elif system_name == "Windows":
        _log.info("Detected Windows architecture.")
        variant = "x86_64-pc-windows-msvc-shared"

    else:
        _log.error(f"Unknown operating system: {system_name}")
        return False

    file_name = f"cpython-{python_version}-{variant}-install_only.tar.gz"
    download_url = f"https://github.com/indygreg/python-build-standalone/releases/download/{date_tag}/{file_name}"

    try:
        _log.info(f"Downloading standalone Python for {system_name} {arch_name}...")
        with urllib.request.urlopen(download_url) as response, open(file_name, "wb") as out_file:
            data = response.read()
            out_file.write(data)

    except Exception as e:
        _log.error(f"Download failed: {e}")
        raise e

    _log.info("Extracting Python...")
    try:
        with tarfile.open(file_name) as tar:
            tar.extractall(path=".")
    except tarfile.TarError as e:
        _log.error(f"Extraction failed: {e}")
        return False
    finally:
        os.remove(file_name)

    _log.info("Python installation completed successfully.")
    return True
