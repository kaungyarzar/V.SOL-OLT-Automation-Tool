from typing import List
from urllib.parse import urlencode

from httpx import AsyncClient

from volt_cli_tool.models import (
    DBA_PROFILE,
    GENERIC_PROFILE,
    LINE_PROFILE,
    ONU_PROFILE,
    TRAFFIC_PROFILE,
)


async def get_olt_info(webclient: AsyncClient, mac: str, username: str) -> dict:
    endpoint = "/oltList/getOltListInfoByCondition"
    query = urlencode({"UserName": username, "UserLevel": "super", "Mac": mac})
    res = await webclient.post(endpoint + f"?{query}")
    olt = res.json()
    return olt[0] if olt else {}


async def save_configs(webclient: AsyncClient, mac: str, ip: str) -> bool:
    endpoint = "/oltSystem/system_deviceManage.do"
    query = urlencode({"Ip": ip, "oltMac": mac, "systemAction": "6"})
    res = await webclient.post(endpoint + f"?{query}")
    return res.json()


async def get_onu_profiles(webclient: AsyncClient, mac: str) -> List:
    endpoint = "/gponProfile/getOnuProTable.do"
    query = urlencode({"oltMac": mac})
    res = await webclient.post(endpoint + f"?{query}")
    return res.json()


async def get_dba_profiles(webclient: AsyncClient, mac: str) -> List:
    endpoint = "/gponProfile/getDbaProTable.do"
    query = urlencode({"oltMac": mac})
    res = await webclient.post(endpoint + f"?{query}")
    return res.json()


async def get_traffic_profiles(webclient: AsyncClient, mac: str) -> List:
    endpoint = "/gponProfile/getTrafficProTable.do"
    query = urlencode({"oltMac": mac})
    res = await webclient.post(endpoint + f"?{query}")
    return res.json()


async def get_line_profiles(webclient: AsyncClient, mac: str) -> List:
    endpoint = "/gponProfile/getLineNamePro.do"
    query = urlencode({"oltMac": mac})
    res = await webclient.post(endpoint + f"?{query}")
    return res.json()


async def delete_onu_profile(
    webclient: AsyncClient, mac: str, profile: GENERIC_PROFILE
) -> bool:
    endpoint = "/gponProfile/setOnuProTable.do"
    query = urlencode(ONU_PROFILE.dump_ems_delete(mac, profile.profile_name))
    res = await webclient.post(endpoint + f"?{query}")
    return res.is_success


async def delete_dba_profile(
    webclient: AsyncClient, mac: str, profile: GENERIC_PROFILE
) -> bool:
    endpoint = "/gponProfile/setDbaProTable.do"
    query = urlencode(DBA_PROFILE.dump_ems_delete(mac, profile.profile_name))
    res = await webclient.post(endpoint + f"?{query}")
    return res.is_success


async def delete_traffic_profile(
    webclient: AsyncClient, mac: str, profile: GENERIC_PROFILE
) -> bool:
    endpoint = "/gponProfile/setTrafficProTable.do"
    query = urlencode(TRAFFIC_PROFILE.dump_ems_delete(mac, profile.profile_name))
    res = await webclient.post(endpoint + f"?{query}")
    return res.is_success


async def delete_line_profile(
    webclient: AsyncClient, mac: str, profile: GENERIC_PROFILE
) -> bool:
    endpoint = "/gponProfile/setLinePTcontPro.do"
    query = urlencode(LINE_PROFILE.dump_ems_delete(mac, profile.profile_name))
    res = await webclient.post(endpoint + f"?{query}")
    return res.is_success


async def set_onu_profile(webclient: AsyncClient, mac: str, onu: ONU_PROFILE) -> bool:
    endpoint = "/gponProfile/setOnuProTable.do"
    query = urlencode(onu.dump_ems_create(olt_mac=mac))
    res = await webclient.post(endpoint + f"?{query}")
    return res.status_code == 200


async def set_dba_profile(webclient: AsyncClient, mac: str, dba: DBA_PROFILE) -> bool:
    endpoint = "/gponProfile/setDbaProTable.do"
    query = urlencode(dba.dump_ems_create(olt_mac=mac))
    res = await webclient.post(endpoint + f"?{query}")
    return res.status_code == 200


async def set_traffic_profile(
    webclient: AsyncClient, mac: str, traffic: TRAFFIC_PROFILE
) -> bool:
    endpoint = "/gponProfile/setTrafficProTable.do"
    query = urlencode(traffic.dump_ems_create(olt_mac=mac))
    res = await webclient.post(endpoint + f"?{query}")
    return res.status_code == 200


async def set_line_profile(
    webclient: AsyncClient, mac: str, line: LINE_PROFILE
) -> bool:
    # Create line profile
    line_endpoint = "/gponProfile/setLinePTcontPro.do"
    line_query = urlencode(line.dump_ems_create(olt_mac=mac))
    res = await webclient.post(line_endpoint + f"?{line_query}")
    if not res.is_success:
        raise RuntimeError("line profile create fail.")

    # Create tconts
    tcont_endpoint = "/gponProfile/setLinePTcontPro.do"
    tcont_query = urlencode(line.dump_ems_tconts_create(olt_mac=mac))
    res = await webclient.post(tcont_endpoint + f"?{tcont_query}")
    if not res.is_success:
        raise RuntimeError("tconts create fail.")

    # Create gemports
    gemport_endpoint = "/gponProfile/setLineGemPro.do"
    gemport_query = urlencode(line.dump_ems_gemports_create(olt_mac=mac))
    res = await webclient.post(gemport_endpoint + f"?{gemport_query}")

    if not res.is_success:
        raise RuntimeError("gemports create fail.")

    # Create services
    if line.service:
        srv_endpoint = "/gponProfile/setLineSrvPro.do"
        srv_query = urlencode(line.dump_ems_services_create(olt_mac=mac))
        res = await webclient.post(srv_endpoint + f"?{srv_query}")

        if not res.is_success:
            raise RuntimeError("services create fail.")

    # Create service ports
    if line.service_port:
        srv_port_endpoint = "/gponProfile/setLineSrvPortPro.do"
        srv_port_query = urlencode(line.dump_ems_service_ports_create(olt_mac=mac))
        res = await webclient.post(srv_port_endpoint + f"?{srv_port_query}")

        if not res.is_success:
            raise RuntimeError("service ports create fail.")
