import asyncio
import dis
import re
import aiosqlite
import sys
import json
import ratings_calc
import display
from cfg import *


async def get_input_async(prompt):
    return await asyncio.get_event_loop().run_in_executor(
        None, input, prompt
    )





def get_last_gid():
    with open(C_GID_SAVE_PATH, "r") as f:
        res = int(f.read())
    return res

def set_last_gid(gid):
    with open(C_GID_SAVE_PATH, "w") as f:
        f.write(str(gid))


# for (k,v) in r0:
#     all_data[k] = json.loads(v)
#True if passes check, false otherwise
def check_blacklist(taglist, blacklist):
    return set(blacklist).isdisjoint(set(taglist))

#Same as above
def check_whitelist(taglist, whitelist):
    return set(whitelist).issubset(set(taglist))

lang_tags_blacklist = [
    "language:vietnamese",
    "language:thai",
    "language:spanish"

]

other_blacklist = [
    "mixed:guro",


    "female:big breasts",
    "female:rape",
    "female:mind control"
]
tags_blacklist = lang_tags_blacklist + other_blacklist
tags_whitelist = [
    "male:sole male",
    "female:sole female",
    "mixed:incest",
]

category_whitelist = ["Manga", "Doujinshi"]
def check_entry(entry):
    tags = entry["tags"]
    category = entry["category"]
    if not category in category_whitelist:
        return False
    if not check_blacklist(tags, tags_blacklist):

        return False
    if not check_whitelist(tags, tags_whitelist):
        return False
    if entry["expunged"]:
        return False
    return True





async def main():
    db0_n = sys.argv[1]


    db0 = await aiosqlite.connect(db0_n)



    order_by_rating = " order by json_extract(resp, '$.rating') desc"
    ignore_expunged = " where json_extract(resp, '$.expunged')=false "
    query = "select * from api_response " + ignore_expunged + order_by_rating #+ " limit 10000"
    res_cursor = await db0.execute(query)
    prefetch_queue = []
    jumpdst = None
    while True:

        while len(prefetch_queue) <= C_PREFETCH_ENTRIES:

            #i hate this
            if jumpdst != None:
                while jumpdst != None:
                    if len(prefetch_queue) > 0:
                        entry = await prefetch_queue.pop(0)
                        if jumpdst == entry["gid"]:
                            jumpdst = None
                            #put it back(lol)
                            prefetch_queue.insert(0, display.prefetch_entry(entry=entry))
                            break
                        continue
                    gid, entry_text = await res_cursor.fetchone()
                    entry = json.loads(entry_text)
                    if gid == jumpdst:
                        jumpdst = None
            else:
                gid, entry_text = await res_cursor.fetchone()
                entry = json.loads(entry_text)

            
            
            if not check_entry(entry):
                continue
            prefetch_queue.append(asyncio.create_task(display.prefetch_entry(entry)))
        res = await prefetch_queue.pop(0)
        await display.print_entry(res)

        inp = await get_input_async("")
        if inp == "q":
            set_last_gid(res["gid"])
            break
        if inp == "jl":
            jumpdst = get_last_gid()
            continue

        #j:gid
        if inp[:2] == "j:":
            jumpdst = int(inp.split(":")[1])
            continue
        
        set_last_gid(res["gid"])
    await db0.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("exiting...")
