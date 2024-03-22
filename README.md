
# NChunk

A simple python script that allows chunked file uploads to a Nextcloud's DAV backend (or probably to anything similar, not tested yet).  
This is far from anything complete, just something i hacked together to finally upload big files to my NC without them timing out all the time or typing endless CURL commands into the terminal. 


## Setup

1. Install Python
2. Clone repo or download zip
3. CD into repo folder
4. (*Optional*) Setup venv
5. Install required packages


  
    

Debian/Ubuntu:
```
sudo apt install python3
python3 --version
git clone https://github.com/Knyllahsyhn/NChunk.git
cd NChunk
python3 -m venv .
source bin/activate
pip install -r requirements.txt

```

Windows(Powershell):
[Python](https://www.python.org/)  
Please consult the official documentation on how to install Python3 correctly and add the exectables to your %PATH%.  
(I don't recommend the *winget* approach as I've experienced broken installations before.)

```
git clone https://github.com/Knyllahsyhn/NChunk.git
cd NChunk
python.exe -m venv . 
Scripts\activate
pip install -r requirements.txt  
```
    
## Usage/Examples

Just run the script using `python3 ./Nchunk.py` (Linux) / `py .\Nchunk.py` (Windows).  

The Script will not accept any command line arguments, instead it will guide you through the process.


## Features

- cross-platform
- credentials saving using the **keyring** package
- GUI file selection
- progress indicator
- asynchronous



## Roadmap

- Extended logging 
- Profile selection
- Fix ugly progress bar
- 2FA Support
- Proper Documentation
- Error Handling
- Tests
- Build complete GUI
- Automatic selection of said GUI or CLI depending on environment
- probably make this into a library at some point for usage in upload clients or whatever



## License

 Licensed under [GPL-3](https://choosealicense.com/licenses/agpl-3.0/).
 Check LICENSE file for more information.


## Appendix

My thanks to @shiftpi whose Javascript Version of a chunked uploader (which is far more professional than this ) inspired me to work on this. 
