import asyncio
import aiosqlite
import sys
import json
from cfg import *
import os
import yappi

batch_size = 4096

async def main():
    db0_n = sys.argv[1]
    db1_n = "cachedb.db" if len(sys.argv) < 3 else sys.argv[2]
    if os.path.exists(db1_n):
        confirm = input(f"operation will overwrite {db1_n}. confirm?(y/n) ")
        if confirm != "y":
            print("not confirmed. exiting...")
            return

    db0 = await aiosqlite.connect(db0_n)
    db1 = await aiosqlite.connect(db1_n)
    _ = await db1.execute("DROP TABLE IF EXISTS api_response")
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
        res_rows = await cursor_read.fetchmany(batch_size)
        if len(res_rows) == 0:
            break
        insert_vals = []
        for res_row in res_rows:
            res_s = res_row[0]
            res = json.loads(res_s)
            #print(res["gid"])
            
            vals = (
                res["gid"], 
                res_s, 
                res["rating"], 
                res["title"], 
                res["title_jpn"],
                json.dumps(res["tags"]),
                1 if res["expunged"] else 0
            ) 
            insert_vals.append(vals)
        command = """
            INSERT OR REPLACE INTO api_response 
            (gid, resp, rating, title, title_jpn, tags_json, expunged)
            VALUES(?, ?, ?, ?, ?, ?, ?)
            """
        cursor_write = await db1.executemany(command, insert_vals)

    await db1.commit()
    await db0.close()
    await db1.close()




if __name__ == "__main__":
    # yappi.set_clock_type("wall")
    # with yappi.run():
    #     asyncio.run(main())
    # stats = yappi.get_func_stats()
    # stats.save("yappi.callgrind", 'callgrind')
    # #stats.print_all()

    asyncio.run(main())
    




