from volt_cli_tool.configs import ENV, get_logger, read_configs
from volt_cli_tool.emsclient import (
    AsyncEMSWebClient,
    delete_dba_profile,
    delete_line_profile,
    delete_onu_profile,
    delete_traffic_profile,
    get_olt_info,
    save_configs,
    set_dba_profile,
    set_line_profile,
    set_onu_profile,
    set_traffic_profile,
)
from volt_cli_tool.models import PROFILES

CFG_INI = read_configs(ENV["APP_CONFIG_INI"])
BASE_URL = CFG_INI.get("ems-server", "base_url")
USERNAME = CFG_INI.get("ems-server", "username")
PASSWORD = CFG_INI.get("ems-server", "password")
TIMEOUT = CFG_INI.getint("ems-server", "timeout")

LOG = get_logger()


async def profile_workflow(data: PROFILES, mac: str):
    async with AsyncEMSWebClient(BASE_URL, USERNAME, PASSWORD, TIMEOUT) as wsclient:
        olt_info = await get_olt_info(wsclient, mac=mac, username=USERNAME)
        if not olt_info:
            raise RuntimeError(f"{mac} not found.")
        LOG.info(
            "olt_info",
            hostname=olt_info.get("sysHostName"),
            sys_fw_ver=olt_info.get("sysFirmVersion"),
            device_type=olt_info.get("deviceType"),
            state=olt_info.get("state"),
        )

        if olt_info.get("state") != "online":
            raise RuntimeError(f"{mac} is offline.")

        # Delete Profiles
        if data.line_profiles and data.line_profiles.delete_profile:
            for each in data.line_profiles.delete_profile:
                LOG.info("delete_line_profile", params=each.model_dump_json())
                await delete_line_profile(wsclient, mac, each)

        if data.traffic_profiles and data.traffic_profiles.delete_profile:
            for each in data.traffic_profiles.delete_profile:
                LOG.info("delete_traffic_profile", params=each.model_dump_json())
                await delete_traffic_profile(wsclient, mac, each)

        if data.dba_profiles and data.dba_profiles.delete_profile:
            for each in data.dba_profiles.delete_profile:
                LOG.info("delete_dba_profile", params=each.model_dump_json())
                await delete_dba_profile(wsclient, mac, each)

        if data.onu_profiles and data.onu_profiles.delete_profile:
            for each in data.onu_profiles.delete_profile:
                LOG.info("delete_onu_profile", params=each.model_dump_json())
                await delete_onu_profile(wsclient, mac, each)

        # Set Profiles
        if data.onu_profiles and data.onu_profiles.set_profile:
            for each in data.onu_profiles.set_profile:
                LOG.info("set_onu_profile", params=each.model_dump_json())
                await set_onu_profile(wsclient, mac, each)

        if data.dba_profiles and data.dba_profiles.set_profile:
            for each in data.dba_profiles.set_profile:
                LOG.info("set_dba_profile", params=each.model_dump_json())
                await set_dba_profile(wsclient, mac, each)

        if data.traffic_profiles and data.traffic_profiles.set_profile:
            for each in data.traffic_profiles.set_profile:
                LOG.info("set_traffic_profile", params=each.model_dump_json())
                await set_traffic_profile(wsclient, mac, each)

        if data.line_profiles and data.line_profiles.set_profile:
            for each in data.line_profiles.set_profile:
                LOG.info("set_line_profile", params=each.model_dump_json())
                await set_line_profile(wsclient, mac, each)

        # Saving configs
        LOG.info("saving_configs")
        await save_configs(wsclient, mac=mac, ip=olt_info.get("ip"))
