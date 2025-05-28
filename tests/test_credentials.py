import pytest
from nchunk.uploader import UploadClient
from nchunk.errors import UploadError
from aioresponses import aioresponses

@pytest.mark.asyncio
async def test_credentials_success(monkeypatch):
    client = UploadClient("https://cloud.example.com", "u", "p", ssl_verify=False)
    with aioresponses() as m:
        url = "https://cloud.example.com/remote.php/dav/files/u/"
        m.post(url, status=207)
        m.add("PROPFIND", url, status=207)

        # monkeypatch _request to bypass auth for test
        async def dummy(*args, **kwargs):
            return b""

        monkeypatch.setattr(client, "_request", dummy)
        await client.test_credentials()

@pytest.mark.asyncio
async def test_credentials_fail(monkeypatch):
    client = UploadClient("https://cloud.example.com", "u", "p", ssl_verify=False)
    async def boom(*args, **kwargs):
        raise UploadError("boom")
    monkeypatch.setattr(client, "_request", boom)
    with pytest.raises(UploadError):
        await client.test_credentials()
