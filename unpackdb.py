import asyncio
import aiosqlite
import sys
import json
from cfg import *
import os
#import yappi



async def main():
    db0_n = sys.argv[1]
    db1_n = "cachedb.db" if len(sys.argv) < 3 else sys.argv[2]
    db0 = await aiosqlite.connect(db0_n)
    db1 = await aiosqlite.connect(db1_n)
    _ = await db1.execute("""CREATE TABLE api_response(
    gid INTEGER,
    resp TEXT,
    rating REAL,
    title TEXT,
    title_jpn TEXT,
    tags_json TEXT,
    expunged INTEGER,
    PRIMARY KEY(gid)
    );
    """)
    cursor_read = await db0.execute("SELECT resp from api_response");

    while True:
        res_row = await cursor_read.fetchone()
        if res_row == None:
            break
        res_s = res_row[0]
        res = json.loads(res_s)
        print(res["gid"])
        command = """
        INSERT OR REPLACE INTO api_response 
        (gid, resp, rating, title, title_jpn, tags_json, expunged)
        VALUES(?, ?, ?, ?, ?, ?, ?)
        """
        vals = (
            res["gid"], 
            res_s, 
            res["rating"], 
            res["title"], 
            res["title_jpn"],
            json.dumps(res["tags"]),
            1 if res["expunged"] else 0
        ) 
        cursor_write = await db1.execute(command, vals)

    await db1.commit()
    await db0.close()
    await db1.close()




if __name__ == "__main__":

    asyncio.run(main())
    




