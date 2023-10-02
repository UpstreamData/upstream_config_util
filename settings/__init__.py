from typing import Any

import toml
import os

from pyasic import settings

BASE_DIR = os.path.dirname(__file__)
SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "settings.toml")

_settings = {
    "ping_retries": 1,
    "ping_timeout": 3,
    "scan_threads": 300,
    "get_miner_retries": 1,
    "get_data_retries": 1,
    "whatsminer_password": "admin",
    "innosilicon_password": "admin",
    "antminer_password": "root",
    "bosminer_password": "root",
    "vnish_password": "admin",
    "goldshell_password": "123456789",
    "reboot_threads": 300,
    "config_threads": 300,
    "log_to_file": False,
    "debug": False,
}

try:
    with open(SETTINGS_FILE, "r") as settings_file:
        cfg_util_settings = toml.loads(settings_file.read())
    for setting in cfg_util_settings:
        _settings[setting] = cfg_util_settings[setting]
except:
    pass

settings.update("network_ping_retries", _settings["ping_retries"])
settings.update("network_ping_timeout", _settings["ping_timeout"])
settings.update("network_scan_threads", _settings["scan_threads"])
settings.update("factory_get_retries", _settings["get_miner_retries"])
settings.update("get_data_retries", _settings["get_data_retries"])
settings.update("default_whatsminer_password", _settings["whatsminer_password"])
settings.update("default_innosilicon_password", _settings["innosilicon_password"])
settings.update("default_antminer_password", _settings["antminer_password"])
settings.update("default_bosminer_password", _settings["bosminer_password"])
settings.update("default_vnish_password", _settings["vnish_password"])
settings.update("default_goldshell_password", _settings["goldshell_password"])


def get(key: str, other: Any = None) -> Any:
    return _settings.get(key, other)


if __name__ == "__main__":
    print(toml.dumps(_settings))
