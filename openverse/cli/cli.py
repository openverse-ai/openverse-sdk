import typer
import getpass
from rich import print
from .auth import login as _login
from .auth import logout as _logout
from .auth import whoami as _whoami
from .api import OpenverseAPI
from .utils import make_tarball


app = typer.Typer(help="Openverse CLI — Manage your AI Environment Repositories")


OPENVERSE_ASCII = r"""
             dBBBBP dBBBBBb  dBBBP  dBBBBb dBP dP  dBBBP dBBBBBb .dBBBBP   dBBBP 
            dB'.BP      dB'            dBP                   dBP BP              
           dB'.BP   dBBBP' dBBP   dBP dBP dB .BP dBBP    dBBBBK' `BBBBb  dBBP    
          dB'.BP   dBP    dBP    dBP dBP  BB.BP dBP     dBP  BB     dBP dBP      
         dBBBBP   dBP    dBBBBP dBP dBP   BBBP dBBBBP  dBP  dB'dBBBBP' dBBBBP    
                                                                                                                                       
                    Create • Simulate • Evolve Agent Environments
"""


@app.command("login")
def login_cmd():
    """Authenticate using an Openverse API token."""
    
    print(f"[bold cyan]{OPENVERSE_ASCII}[/bold cyan]")
    print("[bold]To log in, you need an Openverse API token from:[/bold]")
    print("  https://open-verse.ai/settings/tokens\n")

    # ----------------------------------------------------
    # 1. CHECK IF ALREADY LOGGED IN
    # ----------------------------------------------------
    from .config import load_token
    existing = load_token()

    if existing:
        print(f"[bold yellow]Already logged in as {existing['username']}[/bold yellow]")
        print("[bold yellow]If you want to log in as a different user, run:[/bold yellow]")
        print("  openverse-cli logout\n")
        raise typer.Exit(code=0)

    # ----------------------------------------------------
    # 2. PROMPT FOR TOKEN ONLY IF NOT LOGGED IN
    # ----------------------------------------------------
    token = getpass.getpass("Enter your token (input hidden): ")

    success = _login(token)

    if success:
        print("[bold green]Login successful![/bold green]")
    else:
        print("[bold red]✗ Login failed[/bold red]")
        raise typer.Exit(code=1)



@app.command("logout")
def logout_cmd():
    """Log out of Openverse."""
    _logout()

@app.command("whoami")
def whoami_cmd():
    """Display the currently logged-in user."""
    _whoami()

from requests.exceptions import HTTPError

@app.command("create")
def create(repo: str):
    """Create a new Openverse environment repository."""
    api = OpenverseAPI()

    try:
        response = api.create_repo(repo)
        print(f"[green]✓ Created environment:[/green] {response['repo_url']}")

    except HTTPError as e:
        # Handle 409 Conflict (already exists)
        if e.response is not None and e.response.status_code == 409:
            print(f"[yellow]⚠ Environment '{repo}' already exists.[/yellow]")
            return

        # All other HTTP errors
        print(f"[bold red]✗ Failed to create environment: {e}[/bold red]")

    except Exception as e:
        print(f"[bold red]Unexpected error: {e}[/bold red]")


@app.command("push")
def push(
    repo: str, 
    path: str = typer.Argument("."),
    message: str = typer.Option(
        None,
        "--message",
        "-m",
        help="Optional commit message for the push",
    )
):
    """Push local files to an environment repository."""
    api = OpenverseAPI()
    try:
        tarball = make_tarball(path)
        response = api.push_repo(repo, tarball, commit_message=message)
        print(f"[green]✓ Pushed successfully[/green]")
        print(response)
    except Exception as e:
        print(f"[bold red]Failed to push to repository: {e}[/bold red]")

@app.command("pull")
def pull(repo: str, output: str = "./repo.tar.gz"):
    """Pull an environment repository."""
    api = OpenverseAPI()
    try:
        tarball_bytes = api.pull_repo(repo)
        with open(output, "wb") as f:
            f.write(tarball_bytes)
        print(f"[green]✓ Pulled repository to: {output}[/green]")
    except Exception as e:
        print(f"[bold red]Failed to pull repository: {e}[/bold red]")

if __name__ == "__main__":
    app()