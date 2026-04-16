from dataclasses import dataclass
from typing import Any, Optional
import aiohttp


class RemnaApiError(Exception):
    pass


@dataclass
class RemnaClient:
    base_url: str
    token: str
    timeout: int = 10
    session: Optional[aiohttp.ClientSession] = None

    async def start(self):
        if self.session is None:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )

    async def close(self):
        if self.session:
            await self.session.close()
            self.session = None

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    async def _get_json(self, path: str) -> Any:
        if not self.session:
            raise RuntimeError("Client not started")

        url = f"{self.base_url}{path}"

        async with self.session.get(url, headers=self._headers()) as r:
            if r.status >= 400:
                text = await r.text()
                raise RemnaApiError(f"{r.status}: {text}")
            return await r.json()

    async def list_profiles(self) -> list[dict]:
        data = await self._get_json("/api/config-profiles")

        #print(data.get("response", {}).get("configProfiles", []))

        return data.get("response", {}).get("configProfiles", [])
    
    
    async def update_xray_keys_in_profile(self, payload: dict) -> dict:
        if not self.session:
            raise RuntimeError("Client not started")
        
        url = f"{self.base_url}/api/config-profiles"
        
        async with self.session.patch(
            url, 
            json=payload, 
            headers=self._headers()
        ) as r:
            if r.status >= 400:
                text = await r.text()
                raise RemnaApiError(f"Ошибка обновления профиля: {r.status} {text}")
            
            return await r.json()


