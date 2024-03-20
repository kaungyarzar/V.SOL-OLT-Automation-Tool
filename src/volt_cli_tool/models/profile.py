from typing import List, Literal

from pydantic import BaseModel, Field, field_serializer, model_validator


class TCONT(BaseModel):
    tcont_id: int = Field(ge=0, le=256, serialization_alias="tcontId")
    tcont_name: str = Field(max_length=50, serialization_alias="tcontName")
    dba_profile_name: str = Field(max_length=50, serialization_alias="tcontDbaName")

    def _dump_ems_create(self, line_profile_name: str) -> dict:
        data = self.model_dump(by_alias=True)
        data.update({"action": "ADD", "linePName": line_profile_name})
        return data

    def model_dump_ems(self, line_profile_name: str) -> dict:
        emf_model = {
            "action": "ADD",
            "linePName": line_profile_name,
            "tcontId": self.tcont_id,
            "tcontName": self.tcont_name,
            "tcontDbaName": self.dba_profile_name,
        }
        return emf_model


class GEMPORT(BaseModel):
    gemport_id: int = Field(ge=0, le=256, serialization_alias="gemGId")
    gemport_name: str = Field(max_length=50, serialization_alias="gemName")
    tcont_id: int = Field(ge=0, le=256, serialization_alias="gemTcontId")
    upstream_traffic_profile_name: str = Field(
        max_length=50, serialization_alias="upTraffic"
    )
    downstream_traffic_profile_name: str = Field(
        max_length=50, serialization_alias="dnTraffic"
    )
    cos: int = Field(ge=-1, le=8, default=8, serialization_alias="gemCos")  # 8 is N/A
    up_queue_map_id: int = Field(
        ge=-1, le=4, default=4, serialization_alias="upQmap"
    )  # 4 is N/A
    down_queue_map_id: int = Field(
        ge=-1, le=8, default=8, serialization_alias="dnQmap"
    )  # 8 is N/A
    state: Literal["enable", "disable"] = Field(
        default="enable", serialization_alias="state"
    )

    @field_serializer("state")
    def __serialize_state(self, v: str, _info) -> int:
        return 1 if v == "enable" else 0

    def _dump_ems_create(self, line_profile_name: str) -> dict:
        data = self.model_dump(by_alias=True)
        data.update({"action": 1, "gponLPName": line_profile_name})
        return data


class SERVICE(BaseModel):
    service_name: str = Field(max_length=50, serialization_alias="srvName")
    gemport_id: int = Field(ge=0, le=256, serialization_alias="srvGemId")
    vlan_mode: Literal["Tag", "Untag"] = Field(
        default="Tag", serialization_alias="srvVlanMode"
    )
    vlan_list: int = Field(default="N/A", serialization_alias="srvVlanList")
    cos_list: str = Field(default="N/A", serialization_alias="srvCosList")
    port_type: Literal["N/A", "Eth", "Iphost"] = Field(
        default="N/A", serialization_alias="portType"
    )
    port_num: int = Field(ge=0, default=0, serialization_alias="portNum")

    @field_serializer("port_type")
    def __serialize_port_type(self, v: str, _info) -> int:
        opts = ["N/A", "Eth", "Iphost"]
        return opts.index(v)

    @model_validator(mode="after")
    def __validate_model(self):
        if self.port_type == 1 and self.port_num > 32:
            raise ValueError("port_num is out of range. Eth(1-32)")
        if self.port_type == 2 and self.port_num > 255:
            raise ValueError("port_num is out of range. Iphost(1-255)")

        if self.vlan_mode == "Untag":
            self.vlan_list = "N/A"

        return self

    def _dump_ems_create(self, line_profile_name: str) -> dict:
        data = self.model_dump(by_alias=True)
        data.update({"action": 1, "gponLPName": line_profile_name})
        return data


class SERVICE_PORT(BaseModel):
    service_port_id: int = Field(ge=0, le=129, serialization_alias="srvPortId")
    gemport_id: int = Field(ge=0, le=256, serialization_alias="srvPortGemId")
    user_vlan: int = Field(ge=0, serialization_alias="srvPortUserVlan")
    translate_vlan: int = Field(ge=0, serialization_alias="srvPortTslVlan")
    service_mode: Literal["Cvlan"] = Field(
        default="Cvlan", serialization_alias="srvPortMode"
    )
    translate_cos: int = Field(
        ge=-1, le=8, default=-1, serialization_alias="srvPortTslCos"
    )  # -1 is N/A
    translate_svlan: int = Field(
        ge=0, default=0, serialization_alias="srvPortTslSvlan"
    )  # 0 is N/A
    translate_scos: int = Field(
        ge=-1, le=8, default=-1, serialization_alias="srvPortTslScos"
    )  # -1 is N/A
    description: str = Field(default="N/A", serialization_alias="srvPortDesc")

    @field_serializer("service_mode")
    def __serialize_service_mode(self, v: str, _info):
        opts = ["Cvlan"]
        return opts.index(v)

    def _dump_ems_create(self, line_profile_name: str) -> dict:
        data = self.model_dump(by_alias=True)
        data.update({"action": 1, "gponLPName": line_profile_name})
        return data


class LINE_PROFILE(BaseModel):
    profile_name: str = Field(max_length=50, serialization_alias="linePName")
    tcont: List[TCONT]
    gemport: List[GEMPORT]
    service: List[SERVICE] = Field(default=None)
    service_port: List[SERVICE_PORT] = Field(default=None)

    def dump_ems_create(self, olt_mac: str) -> dict:
        data = self.model_dump(by_alias=True, include={"profile_name"})
        data.update({"action": "CLEAR"})
        return {"oltMac": olt_mac, "list": [data]}

    def dump_ems_tconts_create(self, olt_mac: str) -> dict:
        tconts = []
        for each in self.tcont:
            tconts.append(each._dump_ems_create(self.profile_name))
        return {"oltMac": olt_mac, "list": tconts}

    def dump_ems_gemports_create(self, olt_mac: str) -> dict:
        gemports = []
        for each in self.gemport:
            gemports.append(each._dump_ems_create(self.profile_name))
        return {"oltMac": olt_mac, "list": gemports}

    def dump_ems_services_create(self, olt_mac: str) -> dict:
        services = []
        for each in self.service:
            services.append(each._dump_ems_create(self.profile_name))
        return {"oltMac": olt_mac, "list": services}

    def dump_ems_service_ports_create(self, olt_mac: str) -> dict:
        service_ports = []
        for each in self.service_port:
            service_ports.append(each._dump_ems_create(self.profile_name))
        return {"oltMac": olt_mac, "list": service_ports}

    @classmethod
    def dump_ems_delete(cls, olt_mac: str, profile_name: str) -> dict:
        data = {
            "oltMac": olt_mac,
            "list": [{"linePName": profile_name, "action": "DeleteALL"}],
        }
        return data

    def model_dump_ems_profile(self) -> dict:
        ems_model = {"action": "CLEAR", "linePName": self.profile_name}
        return ems_model

    def model_dump_ems_tconts(self) -> list:
        tconts = []
        for each in self.tcont:
            tconts.append(each.model_dump_ems(self.profile_name))
        return tconts

    def model_dump_ems_gemports(self) -> list:
        gemports = []
        for each in self.gemport:
            gemports.append(each.model_dump_ems(self.profile_name))
        return gemports

    def model_dump_ems_services(self) -> list:
        services = []
        for each in self.service:
            services.append(each.model_dump_ems(self.profile_name))
        return services

    def model_dump_ems_service_ports(self) -> list:
        service_ports = []
        for each in self.service_port:
            service_ports.append(each.model_dump_ems(self.profile_name))
        return service_ports


class TRAFFIC_PROFILE(BaseModel):
    profile_name: str = Field(max_length=50, serialization_alias="trafficPNameShow")
    sir: int = Field(ge=0, le=10000000, serialization_alias="trafficPSirShow")
    pir: int = Field(ge=0, le=10000000, serialization_alias="trafficPPirShow")
    cbs: int = Field(
        ge=-1, le=1025, default=1024, serialization_alias="trafficPCbsShow"
    )
    pbs: int = Field(
        ge=-1, le=1025, default=1024, serialization_alias="trafficPPbsShow"
    )

    def dump_ems_create(self, olt_mac: str) -> dict:
        data = self.model_dump(by_alias=True)
        data.update({"action": "ADD"})
        return {"oltMac": olt_mac, "list": [data]}

    @classmethod
    def dump_ems_delete(cls, olt_mac: str, profile_name: str) -> dict:
        data = {
            "oltMac": olt_mac,
            "list": [{"trafficPNameShow": profile_name, "action": "DELETE"}],
        }
        return data


class DBA_PROFILE(BaseModel):
    profile_name: str = Field(max_length=50, serialization_alias="dbaPNameShow")
    profile_type: int = Field(ge=0, le=6, serialization_alias="dbaPTypeShow")
    fixed: int = Field(
        ge=63, le=2488321, default=None, serialization_alias="dbaPFixedShow"
    )
    assured: int = Field(
        ge=63, le=2488321, default=None, serialization_alias="dbaPAssuredShow"
    )
    maximum: int = Field(
        ge=63, le=2488321, default=None, serialization_alias="dbaPMaximumShow"
    )

    @model_validator(mode="after")
    def __validate_model(self):
        # Check required field values base on profile type [1-5]
        if self.profile_type == 1 and self.fixed is None:
            raise ValueError("Type-1 needs 'fixed' value")
        if self.profile_type == 2 and self.assured is None:
            raise ValueError("Type-2 needs 'assured' value")
        if self.profile_type == 3 and (not self.assured or not self.maximum):
            raise ValueError("Type-3 needs 'assured' and 'maximum' values")
        if self.profile_type == 4 and not self.maximum:
            raise ValueError("Type-4 needs 'maximum' value")
        if self.profile_type == 5 and (
            not self.fixed or not self.assured or not self.maximum
        ):
            raise ValueError("Type-5 needs 'fixed', 'assured' and 'maximum' values")

        # Validate values
        if self.profile_type == 3 and (self.assured > self.maximum):
            raise ValueError("'maximum' must be bigger than 'assured'")
        if self.profile_type == 5 and (
            self.fixed > self.maximum or self.assured > self.maximum
        ):
            raise ValueError("'maximum' must be bigger that 'fixed' and 'assured'")
        return self

    def dump_ems_create(self, olt_mac: str) -> dict:
        data = self.model_dump(by_alias=True, exclude_none=True)
        data.update({"action": "ADD"})
        return {"oltMac": olt_mac, "list": [data]}

    @classmethod
    def dump_ems_delete(cls, olt_mac: str, profile_name: str) -> dict:
        data = {
            "oltMac": olt_mac,
            "list": [{"dbaPNameShow": profile_name, "action": "DELETE"}],
        }
        return data


class ONU_PROFILE(BaseModel):
    profile_name: str = Field(max_length=50, serialization_alias="onuPNameShow")
    description: str = Field(max_length=50, serialization_alias="onuPDescShow")
    max_tcont: int = Field(ge=0, serialization_alias="onuPMaxTcontShow")
    max_gemport: int = Field(ge=0, serialization_alias="onuPMaxGemportShow")
    max_eth: int = Field(ge=0, le=256, default=1, serialization_alias="onuPMaxEthShow")
    max_pots: int = Field(
        ge=-1, le=256, default=0, serialization_alias="onuPMaxPotsShow"
    )
    max_iphost: int = Field(
        ge=-1, le=256, default=2, serialization_alias="onuPMaxIphostShow"
    )
    max_ipv6host: int = Field(
        ge=-1, le=256, default=0, serialization_alias="onuPMaxIpv6hostShow"
    )
    max_veip: int = Field(
        ge=-1, le=128, default=0, serialization_alias="onuPMaxVeipShow"
    )
    service_ability: Literal["disable", "enable"] = Field(
        default="disable",
        serialization_alias="v1600gOnuPSrvAbility",
    )
    service_ability_n1: Literal["no", "yes"] = Field(
        default="yes", serialization_alias="onuPSrvN1Show"
    )
    service_ability_1m: Literal["no", "yes"] = Field(
        default="yes", serialization_alias="onuPSrv1MShow"
    )
    service_ability_1p: Literal["no", "yes"] = Field(
        default="yes", serialization_alias="onuPSrv1PShow"
    )
    wifi_mgmt_via_non_omci: Literal["disable", "enable"] = Field(
        default="disable", serialization_alias="onuPWMNOmciShow"
    )
    omci_send_mode: Literal["async", "sync"] = Field(
        default="async",
        serialization_alias="onuPOmciSendModeShow",
    )
    default_multicast_range: Literal["none", "all_inclusive"] = Field(
        default="none", serialization_alias="onuPDMRangeShow"
    )

    @field_serializer("service_ability")
    def __serialize_service_ability(self, v: str, _info) -> int:
        return 1 if v == "enable" else 0

    @field_serializer("service_ability_n1")
    def __serialize_service_ability_n1(self, v: str, _info) -> int:
        return 1 if v == "yes" else 0

    @field_serializer("service_ability_1m")
    def __serialize_service_ability_1m(self, v: str, _info) -> int:
        return 1 if v == "yes" else 0

    @field_serializer("service_ability_1p")
    def __serialize_service_ability_1p(self, v: str, _info) -> int:
        return 1 if v == "yes" else 0

    @field_serializer("wifi_mgmt_via_non_omci")
    def __serialize_wifi_mgmt_via_non_omci(self, v: str, _info) -> int:
        return 1 if v == "enable" else 0

    @field_serializer("omci_send_mode")
    def __serialize_omci_send_mode(self, v: str, _info) -> int:
        return 1 if v == "sync" else 0

    @field_serializer("default_multicast_range")
    def __serializer_default_multicast_range(self, v: str, _info) -> int:
        return 0 if v == "none" else 1

    def dump_ems_create(self, olt_mac: str) -> dict:
        data = self.model_dump(by_alias=True)
        data.update({"action": "ADD"})
        return {"oltMac": olt_mac, "list": [data]}

    @classmethod
    def dump_ems_delete(cls, olt_mac: str, profile_name: str) -> dict:
        data = {
            "oltMac": olt_mac,
            "list": [{"onuPNameShow": profile_name, "action": "DELETE"}],
        }
        return data


class GENERIC_PROFILE(BaseModel):
    profile_name: str = Field(max_length=50)
