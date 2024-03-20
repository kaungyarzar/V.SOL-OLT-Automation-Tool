import pprint
import sys
from io import TextIOWrapper

from pydantic import ValidationError
from yaml import safe_load

from volt_cli_tool import __version__
from volt_cli_tool.configs import get_logger
from volt_cli_tool.models import CONFIG_YML
from volt_cli_tool.workflows import profile_workflow


def load_configs(yml_file: TextIOWrapper):
    profile_cfgs = safe_load(yml_file)
    return profile_cfgs


def is_valid_yml(yml_file: TextIOWrapper):
    try:
        data = load_configs(yml_file)
        _ = CONFIG_YML(**data)
        print("Valid Config YAML File.")
    except ValidationError as e:
        pprint.pprint(e.errors())
        sys.exit(1)


async def apply_configs(yml_file: TextIOWrapper, olt_mac: str):
    data = load_configs(yml_file)
    configs = CONFIG_YML(**data)
    log = get_logger(contexts={"client_ver": __version__, "olt_mac": olt_mac})
    if configs.profiles:
        log.info("manage_profiles")
        await profile_workflow(configs.profiles, olt_mac)
