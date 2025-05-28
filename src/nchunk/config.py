
from __future__ import annotations
import os
import keyring
from pathlib import Path
from typing import Tuple
from dotenv import load_dotenv

SERVICE_NAME = "nchunk_nextcloud"

def load_env():
    env_path = Path(".env")
    if env_path.exists():
        load_dotenv(env_path)

def save_credentials(url: str, user: str, password: str):
    key = f"{url}::{user}"
    keyring.set_password(SERVICE_NAME, key, password)

def get_credentials(url: str, user: str | None = None) -> Tuple[str, str]:
    load_env()
    if user is None:
        user = os.getenv("NEXTCLOUD_USER", "")
    key = f"{url}::{user}"
    pwd = keyring.get_password(SERVICE_NAME, key)
    if pwd is None:
        pwd = os.getenv("NEXTCLOUD_PASS")
    if user and pwd:
        return user, pwd
    raise RuntimeError("No credentials stored for given URL / user")
