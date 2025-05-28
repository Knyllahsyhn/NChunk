
import typer
from pathlib import Path
from rich.console import Console
import asyncio
from .config import save_credentials, get_credentials
from .progress import get_progress
from .uploader import UploadClient
from typing import List


app = typer.Typer(help="Nextcloud chunked uploader")

console = Console()

@app.command()
def login(url: str = typer.Argument(..., help="Base Nextcloud URL"),
          user: str = typer.Argument(..., help="Username"),
          password: str = typer.Option(..., prompt=True, hide_input=True)):
    """Store credentials in OS keyring"""
    save_credentials(url, user, password)
    console.print("[bold green]Credentials saved successfully!")

@app.command()
def upload(files: List[Path] = typer.Argument(..., exists=True, help="Dateien, die hochgeladen werden"),
           url: str = typer.Option(..., help="Base Nextcloud URL"),
           user: str = typer.Option(..., help="Username"),
           remote_dir: str = typer.Option("", help="Target dir in Nextcloud"),
           chunk_size: int = typer.Option(2 * 1024 * 1024, help="Chunk size in bytes"),
           concurrency: int = typer.Option(4, help="Parallel uploads"),
           insecure: bool = typer.Option(False, help="Disable SSL verify")):
    """Upload one or more files"""
    password = get_credentials(url, user)[1]
    progress = get_progress()
    uploader = UploadClient(url, user, password, chunk_size=chunk_size,
                            ssl_verify=not insecure, progress=progress)
    asyncio.run(uploader.upload(list(files), remote_dir=remote_dir))

if __name__ == "__main__":
    app()
