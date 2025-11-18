import requests
from .config import load_token

BASE_URL = "https://server.open-verse.ai/cli"

class OpenverseAPI:
    def __init__(self):
        self.creds = load_token()
        self.token = self.creds["token"] if self.creds else None

    def _headers(self) -> dict:
        if self.token:
            return {"Authorization": f"Bearer {self.token}"}
        return {}
    
    # ---------------- Authentication ----------------
    def validate_token(self) -> dict:
        r = requests.get(f"{BASE_URL}/auth/validate", headers=self._headers())
        r.raise_for_status() # Raise an error for bad responses
        return r.json()
    
    def login(self, token: str) -> dict:
        r = requests.get(
            f"{BASE_URL}/auth/validate", 
            headers={"Authorization": f"Bearer {token}"}
        )
        r.raise_for_status() # Raise an error for bad responses
        return r.json()
    
    # ---------------- Environments ----------------
    def create_repo(self, env_name: str) -> dict:
        r = requests.post(
            f"{BASE_URL}/env/create",
            headers=self._headers(),
            json={"env_name": env_name},
        )
        r.raise_for_status()
        return r.json()
    
    def push_repo(
        self,
        env_name: str,
        tarball_bytes: bytes,
        commit_message: str | None = None
    ) -> dict:

        files = {
            "tarball": ("repo.tar.gz", tarball_bytes),
        }

        # form fields
        data = {}
        if commit_message:
            data["commit_message"] = commit_message

        r = requests.post(
            f"{BASE_URL}/env/{env_name}/push",
            headers=self._headers(),
            files=files,
            data=data
        )
        r.raise_for_status()
        return r.json()

    
    def pull_repo(self, env_name: str) -> bytes:
        r = requests.get(
            f"{BASE_URL}/env/{env_name}/pull",
            headers=self._headers()
        )
        r.raise_for_status()
        return r.content