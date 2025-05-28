
from __future__ import annotations
import asyncio
import aiohttp
import aiofiles
from pathlib import Path
from typing import Sequence
from .errors import UploadError
from .utils import generate_chunk_dir, ensure_posix
from rich.console import Console
from rich.progress import Progress
from urllib.parse import urlparse, urlunparse,quote

console = Console()

class UploadClient:
    def __init__(self, base_url: str, user: str, password: str,
                 *, chunk_size: int = 2 * 1024 * 1024, retries: int = 5,
                 ssl_verify: bool = True, progress: Progress | None = None):
        parsed = urlparse(base_url if "://" in base_url else f"https://{base_url}")
        if not parsed.path or parsed.path == "/":
            # Standard-WebDAV-Endpunkt von Nextcloud anhängen
            parsed = parsed._replace(path="/remote.php/dav")
        self.base_url = urlunparse(parsed).rstrip("/")
        self.user = user
        self.password = password
        self.chunk_size = chunk_size
        self.retries = retries
        self.ssl = None if ssl_verify else False
        self.progress = progress

    async def _request(self, session: aiohttp.ClientSession, method: str, url: str, **kwargs):
        attempt = 0
        backoff = 1
        while True:
            try:
                async with session.request(method, url, **kwargs) as resp:
                    if 200 <= resp.status < 300:
                        return await resp.read()
                    raise UploadError(f"HTTP {resp.status} for {url}", status=resp.status)
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                attempt += 1
                if attempt > self.retries:
                    raise UploadError(f"Failed {method} {url}: {e}") from e
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 30)

    async def _upload_chunks(self, session: aiohttp.ClientSession, local: Path, remote_chunk_dir: str, task_id: int):
            # index=1
            # while True:
            #     data = await f.read(self.chunk_size)
            #     if not data:
            #         break
            #     #end = offset + len(data) - 1
            #     headers = {
            #        # "OC-Chunk-Size": str(self.chunk_size),
            #         #"Content-Range": f"bytes {offset}-{end}/*"
            #         "OC-Chunk-Size": str(self.chunk_size),
            #         "Content-Type": "application/octet-stream"
            #     }
            #     chunk_url = f"{remote_chunk_dir}/{index}"
            #     await self._request(session, "PUT", chunk_url, data=data, headers=headers)
            #     self.progress.update(task_id, advance=len(data))
            #     index += 1
        size      = local.stat().st_size
        digits    = len(str(size))                 # z. B. 9 bei 1 234 567 890
        offset    = 0
        async with aiofiles.open(local, "rb") as f:
            while True:
                data = await f.read(self.chunk_size)
                if not data:
                    break

                end = offset + len(data) - 1       # inkl. letztes Byte
                name = f"{offset:0{digits}d}-{end:0{digits}d}"
                chunk_url = f"{remote_chunk_dir}/{name}"

                headers = {
                    "OC-Chunk-Size": str(self.chunk_size),
                    "Content-Type":  "application/octet-stream",
                }
                await self._request(session, "PUT", chunk_url,
                                    data=data, headers=headers)
                self.progress.update(task_id, advance=len(data))
                offset = end + 1

    async def _assemble_file(self, session: aiohttp.ClientSession, remote_chunk_dir: str, final_path: str):
        move_headers = {"Destination": final_path}
        await self._request(session, "MOVE", remote_chunk_dir, headers=move_headers)

    async def upload(self, local_paths: Sequence[Path], remote_dir: str = ""):
        connector = aiohttp.TCPConnector(ssl=self.ssl, limit=8)
        async with aiohttp.ClientSession(auth=aiohttp.BasicAuth(self.user, self.password),
                                         connector=connector) as session:
            with self.progress:
                tasks = []
                for p in local_paths:
                    chunk_dir = generate_chunk_dir(self.base_url, self.user)
                    #remote_target = f"{self.base_url}/files/{self.user}/{remote_dir}/{p.name}".replace("//", "/")
                    base = self.base_url.rstrip("/")          # .../remote.php/dav   (ohne End-Slash)

                    remote_dir = remote_dir.strip("/")        # ""  oder "Backups"
                    parts = [base, "files", self.user]
                    if remote_dir:
                        parts.append(remote_dir)
                    parts.append(p.name)

                    remote_target = quote("/".join(parts), safe="/:")
                    
                    task_id = self.progress.add_task("upload", filename=p.name, total=p.stat().st_size)
                    t = asyncio.create_task(self._single_file(session, p, chunk_dir, remote_target, task_id))
                    tasks.append(t)
                await asyncio.gather(*tasks)

    async def _single_file(self, session: aiohttp.ClientSession, local: Path, chunk_dir: str, remote_target: str, task_id: int):
        # create chunk dir
        await self._request(session, "MKCOL", chunk_dir)
        await self._upload_chunks(session, local, chunk_dir, task_id)
        await self._assemble_file(session, chunk_dir, remote_target)
        self.progress.update(task_id, completed=True)
        console.print(f"[green]Uploaded {local.name} -> {remote_target}")
