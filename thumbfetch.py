import aiohttp
import os
from cfg import *
import subprocess
import sys


async def _fetch_data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.read()
                return data
            else:
                raise RuntimeError("Fetch request failed")

def _get_thumb_path(gid):
    return f"{C_THUMBCACHE_DIR}/{gid}"

async def _lookup_or_fetch(gid, url):
    #print(url)
    thumbpath = _get_thumb_path(gid)
    os.makedirs(C_THUMBCACHE_DIR, exist_ok=True)
    if os.path.exists(thumbpath):
        return thumbpath
    await _fetch_image(gid, url)
    return thumbpath


async def _fetch_image(gid, url):
    data = await _fetch_data(url)
    thumbpath = _get_thumb_path(gid)
    with open(thumbpath, "wb") as f:
        f.write(data)
     

async def print_image(gid, url):
    #TODO: use coroutine
    p = subprocess.run(["/usr/bin/kitty", "icat", "--scale-up", await _lookup_or_fetch(gid, url)])
    #sys.stdout.write(p)


