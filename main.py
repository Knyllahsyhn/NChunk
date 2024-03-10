import os
import aiohttp
import asyncio
import hashlib
import keyring
from getpass import getpass
from pathlib import *
from tqdm import tqdm
import tkinter as tk
import tkinter.filedialog as fd

class Upload:
    def __init__(self, url, userspace, username, password):
        self.upload_url = f"{url.rstrip('/')}/uploads/{userspace}"
        self.files_url = f"{url.rstrip('/')}/files/{userspace}"
        self.auth = aiohttp.BasicAuth(username, password)

    async def _create_dir(self, remote_path):
        async with aiohttp.ClientSession(auth=self.auth) as session:
            async with session.request("MKCOL", remote_path) as response:
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
                                    data=chunk
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
def store_credentials (username,password):
    keyring.set_password("upload_script","username",username)
    keyring.set_password("upload_script","password",password)

def get_stored_credentials():
    username = keyring.get_password("upload_script","username")
    password = keyring.get_password("upload_script","password")
    return username,password 
 
            
def query_yes_no(question, default="yes"):
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        print(question + prompt)
        choice = input().lower()
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            print("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")

async def main():
    #root = tk.Tk()
    path_home = Path.home()
    surl = input("Enter the URL: ")
    url = f"https://{surl}/remote.php/dav/"
    # username = input("Enter your username: ")
    # password = getpass("Enter your password: ")
    stored_username, stored_password = get_stored_credentials()
    if stored_username and stored_password:
        if query_yes_no("Use stored credentials?"):
            username = stored_username
            password = stored_password
    else:
        username = input("Enter your username: ")
        password = getpass("Enter your password: ")
        if query_yes_no("Store credentials?"):
            store_credentials(username,password)
    userspace = input("Enter the userspace: ")

    upload = Upload(url=url, userspace=userspace, username=username, password=password)
    root = tk.Tk()
    local_files = list(fd.askopenfilenames(parent=root, title= "Bitte Dateien auswählen",initialdir=path_home))
    local_files =[PurePath(x) for x in local_files]
    upload_dir = input("Bitte Upload-Pfad eingeben: ")
    upload_paths = dict(zip(local_files, [str(PurePosixPath(upload_dir,x.name)) for x in local_files]))      #using pathlib for easily formatting the upload path 
          
    
    # local_path = Path(input("Enter the local path of the file to upload: ").strip())
    # while not local_path.exists():
    #     print("Invalid path, please try again!")
    #     local_path = Path(input().strip())

    
    # remote_path = input("Enter the remote path where the file will be uploaded: ").strip()
    # while not remote_path:
    #     question = "Do you want to use the local file name as upload path? (Will be uploaded to root)"
    #     if query_yes_no(question):
    #         remote_path = str(local_path.name)
    #     else:
    #         remote_path = input("Please input valid remote path")



    async def upload_task(local_path,remote_path):
        try:
            await upload.upload_file(local_path=local_path, remote_path=remote_path)
            print("File uploaded successfully!")
        except Exception as e:
            print(f"An error occurred: {e}")
    upload_tasks = [upload_task(k, v) for k,v in upload_paths.items()]
    await asyncio.gather(*upload_tasks)

if __name__ =="__main__":
    asyncio.run(main())