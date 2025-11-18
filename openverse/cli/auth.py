from rich import print
from .config import save_token, delete_token, load_token
from .api import OpenverseAPI
import requests


def login(token: str) -> bool:
    """Authenticate via the Openverse Personal Access Token."""
    existing = load_token()

    # Already logged in with the same token
    if existing and existing.get("token") == token:
        print(f"[bold yellow]Already logged in as {existing['username']}[/bold yellow]")
        return True

    # Logged in but using a different token
    if existing and existing.get("token") != token:
        print(
            f"[bold yellow]You are already logged in as {existing['username']}.[/bold yellow]\n"
            f"[bold yellow]Logging in will replace your existing token.[/bold yellow]"
        )

    api = OpenverseAPI()

    try:
        user_info = api.login(token)
        save_token(token, user_info["username"])
        print(f"[bold green]✓ Logged in as {user_info['username']}[/bold green]")
        return True

    except requests.HTTPError as e:
        if e.response.status_code == 401:
            print("[bold red]✗ Invalid or revoked API token[/bold red]")
            return False
        print(f"[bold red]Login failed: {e}[/bold red]")
        return False

    except Exception as e:
        print(f"[bold red]Unexpected error: {e}[/bold red]")
        return False


def logout() -> None:
    """Log out by deleting the stored token."""
    existing = load_token()

    if not existing:
        print("[yellow]You are not logged in.[/yellow]")
        return

    delete_token()
    print("[bold green]✓ Logged out successfully[/bold green]")


def whoami() -> None:
    """Display the currently logged-in user."""
    creds = load_token()

    if not creds:
        print("[red]Not logged in[/red]")
    else:
        print(f"[bold green]Logged in as {creds['username']}[/bold green]")