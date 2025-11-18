import json
from pathlib import Path

CONFIG_DIR=Path.home() / ".openverse"
TOKEN_FILE=CONFIG_DIR / "token.json"

def save_token(token: str, username: str) -> None:
    """Save the token and username locally."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(TOKEN_FILE, "w") as f:
        json.dump({"token": token, "username": username}, f)

def load_token() -> dict | None:
    """Load the token and username from local disk."""
    if TOKEN_FILE.exists():
        with open(TOKEN_FILE, "r") as f:
            return json.load(f)
    return None

def delete_token() -> None:
    """Remove the stored token and username."""
    if TOKEN_FILE.exists():
        TOKEN_FILE.unlink()