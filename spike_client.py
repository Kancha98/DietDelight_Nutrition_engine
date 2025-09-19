import os
import hmac
import hashlib
from typing import Optional, Dict, Any
import requests

SPIKE_BASE_URL = "https://app-api.spikeapi.com/v3"

class SpikeClient:
    def __init__(self, application_id: str, hmac_key: str, base_url: str = SPIKE_BASE_URL):
        self.application_id = str(application_id)
        self.hmac_key = hmac_key.encode()
        self.base_url = base_url.rstrip("/")

    def sign_user(self, user_id: str) -> str:
        """Generate an HMAC-SHA256 signature for a given user_id."""
        h = hmac.new(self.hmac_key, user_id.encode(), hashlib.sha256)
        return h.hexdigest()

    def get_access_token(self, application_user_id: str) -> str:
        """Exchange signature for an access token using Spike HMAC auth."""
        signature = self.sign_user(application_user_id)
        url = f"{self.base_url}/auth/hmac"
        payload = {
            "application_id": int(self.application_id) if self.application_id.isdigit() else self.application_id,
            "application_user_id": application_user_id,
            "signature": signature,
        }
        resp = requests.post(url, json=payload, headers={"Accept": "application/json"})
        if not resp.ok:
            raise RuntimeError(f"Spike auth failed ({resp.status_code}): {resp.text}")
        data = resp.json()
        token = data.get("access_token")
        if not token:
            raise RuntimeError("No access_token returned from Spike.")
        return token

    def get_userinfo(self, access_token: str) -> Dict[str, Any]:
        """Call /userinfo with the provided token."""
        url = f"{self.base_url}/userinfo"
        resp = requests.get(url, headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        })
        if not resp.ok:
            raise RuntimeError(f"Spike /userinfo failed ({resp.status_code}): {resp.text}")
        return resp.json()

    def api_get(self, path: str, access_token: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generic GET helper for other Spike endpoints, e.g. /timeseries, /interval-stats, etc."""
        path = path.lstrip("/")
        url = f"{self.base_url}/{path}"
        resp = requests.get(url, params=params, headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        })
        if not resp.ok:
            raise RuntimeError(f"Spike GET {path} failed ({resp.status_code}): {resp.text}")
        return resp.json()
