import os 
import aiohttp
import hashlib
from tqdm import tqdm



class Upload:
    def __init__(self, url, userspace, username, password):
        self.upload_url = f"{url.rstrip('/')}/uploads/{userspace}"
        self.files_url = f"{url.rstrip('/')}/files/{userspace}"
        self.auth = aiohttp.BasicAuth(username, password)

    async def _create_dir(self, remote_path):
        async with aiohttp.ClientSession(auth=self.auth) as session:
            async with session.request("MKCOL", remote_path,verify_ssl=False) as response:
                response.raise_for_status()

    async def _create_dirs_recursively(self, remote_path):
        dirs = [p for p in remote_path.split('/') if p]
        if not dirs:
            return
        current_path = ''
        for d in dirs:
            current_path += f'/{d}'
            try:
                await self._create_dir(f"{self.files_url}{current_path}")

            except aiohttp.ClientResponseError as e:
                if not e.text or '<s:message>The resource you tried to create already exists</s:message>' not in e.text:
                    raise e

    async def upload_file(self, local_path, remote_path, chunk_size=2 * 1024 * 1024, retry_chunks=5, create_dirs_recursively=False):
        chunk_path = f"{self.upload_url}/{hashlib.sha256(os.urandom(32)).hexdigest()}"
        await self._create_dir(chunk_path)

        identifier_length = len(str(os.path.getsize(local_path)))

        with open(local_path, 'rb') as f:
            chunk_no = 0
            chunk_offset = 0
            file_size = os.path.getsize(local_path)

            with tqdm(total=file_size,unit='B',unit_scale=True,desc=f"Uploading {local_path}",ascii=True) as pbar:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    offset_identifier = str(chunk_offset).zfill(identifier_length)
                    chunk_offset += len(chunk) - 1
                    limit_identifier = str(chunk_offset).zfill(identifier_length)
                    chunk_offset += 1

                    success = False
                    last_http_error_event = None
                    for i in range(retry_chunks + 1):
                        async with aiohttp.ClientSession(auth=self.auth) as session:
                            try:
                                async with session.put(
                                    f"{chunk_path}/{offset_identifier}-{limit_identifier}",
                                    data=chunk,verify_ssl=False
                                ) as response:
                                    response.raise_for_status()
                                    success = True
                                    break
                            except aiohttp.ClientResponseError as e:
                                last_http_error_event = e

                    if not success:
                        raise RuntimeError(f"Failed uploading chunk {chunk_no}, max retries reached: {last_http_error_event}")

                    chunk_no += 1
                    pbar.update(len(chunk))        

        if create_dirs_recursively:
            remote_dir = os.path.dirname(remote_path)
            await self._create_dirs_recursively(remote_dir)

        async with aiohttp.ClientSession(auth=self.auth) as session:
            try:
                async with session.request(
                    "MOVE",
                    f"{chunk_path}/.file",
                    headers={"Destination": f"{self.files_url}/{remote_path.lstrip('/')}"}
                ) as response:
                    response.raise_for_status()
            except aiohttp.ClientResponseError as e:
                raise RuntimeError(f"Failed to glue the chunks together: {e}")