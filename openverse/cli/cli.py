import typer
import getpass
from rich import print
from .auth import login as _login
from .auth import logout as _logout
from .auth import whoami as _whoami
from .api import OpenverseAPI
from .utils import make_tarball, normalize_repo_path
import os
import tarfile
import tempfile
import shutil
from requests.exceptions import HTTPError

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
    HuggingFace-style push:

    openverse-cli push repo ./folder ./remote
      → repo/remote/<folder contents>

    openverse-cli push repo ./file.py ./remote/file.py
      → repo/remote/file.py

    openverse-cli push repo ./folder
      → repo/<folder contents>
    """

    api = OpenverseAPI()

    if not os.path.exists(local_path):
        print(f"[red]✗ Local path does not exist: {local_path}[/red]")
        raise typer.Exit(1)

    # --- normalise remote path (strip './', treat as folder unless single file)
    if remote_path:
        try:
            clean_remote_path = normalize_repo_path(remote_path)
            if clean_remote_path in [".", ""]:  # ADD THIS
                clean_remote_path = ""
        except Exception as e:
            print(f"[red]✗ Invalid remote_path: {e}[/red]")
            raise typer.Exit(1)
    else:
        clean_remote_path = ""


    # --- build temp folder to construct tarball
    tmp_dir = tempfile.mkdtemp()

    # compute the final target directory in tarball:
    # tmp_dir/<clean_remote_path>
    target_root = os.path.join(tmp_dir, clean_remote_path)
    os.makedirs(target_root, exist_ok=True)

    # --- local path is file → remote_path treated as file
    if os.path.isfile(local_path):
        # if remote_path ends with '/', prevent it
        if clean_remote_path.endswith("/"):
            print("[red]✗ Remote path cannot end with '/': specify a filename[/red]")
            raise typer.Exit(1)

        shutil.copy2(local_path, target_root)

    else:
        # --- local path is directory → copy contents, not folder itself
        for item in os.listdir(local_path):
            src_item = os.path.join(local_path, item)
            dst_item = os.path.join(target_root, item)

            if os.path.isdir(src_item):
                shutil.copytree(src_item, dst_item, dirs_exist_ok=True)
            else:
                shutil.copy2(src_item, dst_item)

    # --- Now tar the tmp_dir
    tarball = make_tarball(tmp_dir)

    # --- Send to server
    try:
        response = api.push_repo(
            repo,
            tarball,
            commit_message=message,
            remote_path=clean_remote_path if clean_remote_path else None,
        )
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

@app.command("delete")
def delete(repo: str, path: str):
    """
    Delete a file or folder from an environment repo on the hub.
    HuggingFace-style deletion.
    """

    api = OpenverseAPI()

    print(f"🗑 Deleting '{path}' in environment '{repo}'...")

    try:
        try:
            clean_path = normalize_repo_path(path)
        except Exception as e:
            print(f"[red]✗ Invalid path: {e}[/red]")
            raise typer.Exit(1)

        result = api.delete_path(repo, clean_path)
        print("✓ Deleted successfully")
        print(result)

    except HTTPError as e:
        print(f"❌ Failed: {e.response.text}")
        raise typer.Exit(1)

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        raise typer.Exit(1)

if __name__ == "__main__":
    app()