import asyncio

import click
from click_params import MAC_ADDRESS

from volt_cli_tool.app import apply_configs, is_valid_yml


@click.group(invoke_without_command=True, no_args_is_help=True)
@click.version_option()
def entrypoint():
    pass


@entrypoint.command()
@click.argument("config-yml", type=click.File("r"))
@click.argument("olt-mac", type=MAC_ADDRESS)
def apply_config(config_yml, olt_mac):
    """Apply Configs to Device."""
    mac_unix = olt_mac.lower().replace("-", ":")
    asyncio.run(apply_configs(config_yml, mac_unix))


@entrypoint.command()
@click.argument("config_yml_file", type=click.File("r"))
def check_config(config_yml_file):
    """Check YAML Config."""
    is_valid_yml(config_yml_file)
