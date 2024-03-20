import configparser
from functools import lru_cache
from os import getenv
from os.path import isfile

import structlog

ENV = {"APP_CONFIG_INI": getenv("APP_CONFIG_INI", "./volt-cli-config.ini")}


def get_logger(contexts: dict = None):
    if contexts:
        structlog.contextvars.bind_contextvars(**contexts)
    return structlog.getLogger()


@lru_cache
def read_configs(config_ini: str):
    if not isfile(config_ini):
        raise FileNotFoundError(f"File: {config_ini}.")
    config = configparser.ConfigParser()
    config.read(config_ini)
    return config
