import asyncio
from getpass import getpass
from pathlib import *
import tkinter as tk
import tkinter.filedialog as fd
import ux,creds,Upload




            


async def main():
    #root = tk.Tk()
    path_home = Path.home()
    surl = input("Enter the URL: ")
    url = f"https://{surl}/remote.php/dav/"
    # username = input("Enter your username: ")
    # password = getpass("Enter your password: ")
    kr = "upload_script"
    stored_username, stored_password = creds.get_stored_credentials(kr)
    if stored_username and stored_password:
        if ux.query_yes_no("Use stored credentials?"):
            username = stored_username
            password = stored_password
    else:
        username = input("Enter your username: ")
        password = getpass("Enter your password: ")
        if ux.query_yes_no("Store credentials?"):
            creds.store_credentials(kr,username,password)
    userspace = input("Enter the userspace: ")

    upload = Upload.Upload(url=url, userspace=userspace, username=username, password=password)
    root = tk.Tk()
    local_files = list(fd.askopenfilenames(parent=root, title= "Bitte Dateien auswählen",initialdir=path_home))
    local_files =[PurePath(x) for x in local_files]
    upload_dir = input("Enter Upload Path: (if none specified, files will be uploaded to root)" )
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