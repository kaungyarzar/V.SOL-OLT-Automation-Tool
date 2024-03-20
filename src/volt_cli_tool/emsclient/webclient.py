from contextlib import asynccontextmanager
from typing import Generator

import httpx
from pydantic import BaseModel

from volt_cli_tool import __version__


class AuthCredentials(BaseModel):
    loginname: str
    loginpass: str


class LogoutPayload(BaseModel):
    loginName: str
    loginStatus: int = 1
    loginType: int = 0


class LoginFail(Exception):
    pass


@asynccontextmanager
async def AsyncEMSWebClient(
    base_url: str, username: str, password: str, timeout: int = 10
) -> Generator[httpx.AsyncClient, None, None]:
    login_payload = AuthCredentials(loginname=username, loginpass=password)
    logout_payload = LogoutPayload(loginName=username)
    headers = {"user-agent": f"volt_cli_tool/{__version__}"}

    def is_login(html: str):
        fail_pattern = "<title>Login</title>"
        return True if html.find(fail_pattern) == -1 else False

    async with httpx.AsyncClient(
        base_url=base_url, headers=headers, timeout=timeout
    ) as client:
        # Login Session
        r = await client.post("/uc/login", data=login_payload.model_dump())

        if not is_login(r.content.decode()):
            raise LoginFail("login failed.")

        yield client

        # Logout Session
        await client.post("/uc/loginLog.do", data=logout_payload.model_dump())
