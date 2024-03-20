from typing import List

from pydantic import BaseModel, Field

from .profile import (
    DBA_PROFILE,
    GENERIC_PROFILE,
    LINE_PROFILE,
    ONU_PROFILE,
    TRAFFIC_PROFILE,
)


class ONU_PROFILES(BaseModel):
    set_profile: List[ONU_PROFILE] = Field(default=None)
    delete_profile: List[GENERIC_PROFILE] = Field(default=None)


class DBA_PROFILES(BaseModel):
    set_profile: List[DBA_PROFILE] = Field(default=None)
    delete_profile: List[GENERIC_PROFILE] = Field(default=None)


class TRAFFIC_PROFILES(BaseModel):
    set_profile: List[TRAFFIC_PROFILE] = Field(default=None)
    delete_profile: List[GENERIC_PROFILE] = Field(default=None)


class LINE_PROFILES(BaseModel):
    set_profile: List[LINE_PROFILE] = Field(default=None)
    delete_profile: List[GENERIC_PROFILE] = Field(default=None)


class PROFILES(BaseModel):
    onu_profiles: ONU_PROFILES = Field(default=None)
    dba_profiles: DBA_PROFILES = Field(default=None)
    traffic_profiles: TRAFFIC_PROFILES = Field(default=None)
    line_profiles: LINE_PROFILES = Field(default=None)


class CONFIG_YML(BaseModel):
    profiles: PROFILES = Field(default=None)
