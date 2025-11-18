import typer
import getpass
from rich import print
from .auth import login as _login
from .auth import logout as _logout
from .auth import whoami as _whoami
from .api import OpenverseAPI
from .utils import make_tarball
import os
import tarfile
import tempfile
import shutil


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

    # 1. CHECK IF ALREADY LOGGED IN
    from .config import load_token
    existing = load_token()

    if existing:
        print(f"[bold yellow]Already logged in as {existing['username']}[/bold yellow]")
        print("[bold yellow]If you want to log in as a different user, run:[/bold yellow]")
        print("  openverse-cli logout\n")
        raise typer.Exit(code=0)

    # 2. PROMPT FOR TOKEN ONLY IF NOT LOGGED IN
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
    local_path: str = typer.Argument("."),
    remote_path: str = typer.Argument(None),
    message: str = typer.Option(
        None,
        "--message",
        "-m",
        help="Optional commit message for the push",
    )
):
    """
    Push local files to an environment repository.

    Usage:
      openverse-cli push repo .                       → push entire folder
      openverse-cli push repo ./file.txt              → push single file to root
      openverse-cli push repo ./a/b.txt x/y/z.txt     → push into subfolder x/y/z.txt
    """

    api = OpenverseAPI()

    # CASE A — User provided remote path
    if remote_path is not None:

        if not os.path.exists(local_path):
            print(f"[red]✗ Local path does not exist: {local_path}[/red]")
            raise typer.Exit(code=1)

        # Create a temp structure that mirrors what the server expects
        tmp_dir = tempfile.mkdtemp()
        target_file_path = os.path.join(tmp_dir, remote_path)

        # Ensure all parent folders exist
        os.makedirs(os.path.dirname(target_file_path), exist_ok=True)

        # Copy single file or entire folder structure
        if os.path.isfile(local_path):
            shutil.copy2(local_path, target_file_path)
        else:
            # Copy entire folder into remote subfolder
            shutil.copytree(local_path, os.path.dirname(target_file_path), dirs_exist_ok=True)

        # Create tarball from temp structure
        tarball = make_tarball(tmp_dir)

    else:

        # CASE B — Standard push (directory or file)
        if not os.path.exists(local_path):
            print(f"[red]✗ Local path does not exist: {local_path}[/red]")
            raise typer.Exit(code=1)

        tarball = make_tarball(local_path)

    # Perform the push
    try:
        response = api.push_repo(repo, tarball, commit_message=message)
        print(f"[green]✓ Pushed successfully[/green]")
        print(response)
    except Exception as e:
        print(f"[bold red]Failed to push to repository: {e}[/bold red]")


@app.command("pull")
def pull(repo: str, destination: str = typer.Argument(".")):
    """
    Pull an Openverse environment repository into a folder.

    HuggingFace-like behavior:
    - openverse-cli pull env     -> ./env/
    - openverse-cli pull env dir -> dir/env/
    """

    api = OpenverseAPI()

    # Resolve destination
    destination = os.path.abspath(destination)

    # Default case → create ./repo/
    if destination == os.path.abspath("."):
        target_root = os.path.join(destination, repo)
    else:
        os.makedirs(destination, exist_ok=True)
        target_root = os.path.join(destination, repo)

    os.makedirs(target_root, exist_ok=True)

    try:
        # Download tarball
        tarball_bytes = api.pull_repo(repo)

        # Extract to temp directory
        tmp_dir = tempfile.mkdtemp()
        tar_path = os.path.join(tmp_dir, "repo.tar.gz")

        with open(tar_path, "wb") as f:
            f.write(tarball_bytes)

        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(tmp_dir)

        # Tar contains a folder named <repo>
        extracted_repo_dir = os.path.join(tmp_dir, repo)

        if not os.path.isdir(extracted_repo_dir):
            raise Exception("Unexpected archive structure: missing repo folder")

        # Merge extracted repo into target_root
        for root, dirs, files in os.walk(extracted_repo_dir):
            rel = os.path.relpath(root, extracted_repo_dir)
            dest_dir = os.path.join(target_root, rel) if rel != "." else target_root

            os.makedirs(dest_dir, exist_ok=True)

            for f in files:
                shutil.copy2(
                    os.path.join(root, f),
                    os.path.join(dest_dir, f)
                )

        print(f"[green]✓ Pulled environment into:[/green] {target_root}")

    except HTTPError as e:
        status = e.response.status_code if e.response else None

        if status == 404:
            print(f"[yellow]⚠ Environment '{repo}' does not exist.[/yellow]")
            return

        if status == 403:
            print(f"[red]✗ No permission to pull '{repo}'.[/red]")
            return

        print(f"[red]✗ Failed to pull environment: {e}[/red]")

    except Exception as e:
        print(f"[bold red]Unexpected error: {e}[/bold red]")

if __name__ == "__main__":
    app()