import asyncio
import glob
import aiosqlite
import sys
import json
import lib.display as display
from cfg import *
import os
import argparse

from lib.ehutils import ALL_NAMESPACES


async def get_input_async(prompt):
    return await asyncio.get_event_loop().run_in_executor(
        None, input, prompt
    )


def split_tag(tag):
    if ":" in tag:
        return tuple(tag.split(":"))
    return ("", tag)

def get_last_gid():
    if not os.path.exists(C_GID_SAVE_PATH):
        return None
    with open(C_GID_SAVE_PATH, "r") as f:
        res = int(f.read())
    return res

def set_last_gid(gid):
    with open(C_GID_SAVE_PATH, "w") as f:
        f.write(str(gid))


# for (k,v) in r0:
#     all_data[k] = json.loads(v)
#True if passes check, false otherwise
def check_single_tag_match(tag : str, taglist : list):
    namespace, name = split_tag(tag)
    for dsttag in taglist:
        dstns, dstname = split_tag(dsttag)
        if namespace != "*":
            if namespace != dstns:
                continue
        if name != "*":
            if name != dstname:
                continue
        return True
    return False

def check_blacklist(taglist : list[str], blacklist : set[str]):
    #for t in blacklist:
    #    if check_single_tag_match(t, taglist):
    #        return False
    #return True
    return blacklist.isdisjoint(set(taglist))

#Same as above
def check_whitelist(taglist : list[str], whitelist : set[str]):
    #for t in whitelist:
    #    if not check_single_tag_match(t, taglist):
    #        return False
    #return True
    return whitelist.issubset(set(taglist))




tags_whitelist = set()
tags_blacklist = set()

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


def read_to_list(filename : str):
    dst = []
    with open(filename, "r") as f:
        while True:
            res = f.readline()
            if res == "":
                break
            res = res.strip()
            if res == "":
                continue
            dst.append(res)
    return dst


def expand_tag(tag):
    ns, v = split_tag(tag)
    if ns == "":
        return [tag]
    if ns == "*":
        res = []
        for k in set(ALL_NAMESPACES.values()):
            res.append(f"{k}:{v}")
        return res
    return [f"{ALL_NAMESPACES[ns]}:{v}"]

def expand_filter_set(filter_set : set[str]):
    new_set = set()
    for t in filter_set:
        for et in expand_tag(t):
            new_set.add(et)
    return new_set
        
    


def init_filters(whitelist, blacklist):
    global tags_whitelist
    global tags_blacklist
    tags_whitelist = set(read_to_list(whitelist))
    tags_blacklist  = set(read_to_list(blacklist))

    tags_whitelist = expand_filter_set(tags_whitelist)
    tags_blacklist = expand_filter_set(tags_blacklist)
    




async def main():
    parser = argparse.ArgumentParser(
        description="ehdb browser"
    )
    parser.add_argument("-d", "--database", default="cachedb.db")
    parser.add_argument("-w", "--whitelist", default="whitelist.txt")
    parser.add_argument("-b", "--blacklist", default="blacklist.txt")

    args = parser.parse_args(sys.argv[1:])
    db0_n = args.database
    init_filters(args.whitelist, args.blacklist)


    db0 = await aiosqlite.connect(db0_n)
    

    #order_by_rating = " order by json_extract(resp, '$.rating') desc"
    order_by_rating = " order by rating desc "
    #ignore_expunged = " where json_extract(resp, '$.expunged')=false "
    ignore_expunged = " where expunged=0 "
    query = "select gid, resp from api_response " + ignore_expunged + order_by_rating #+ " limit 10000"
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
                            prefetch_queue.insert(0, asyncio.create_task(display.prefetch_entry(entry=entry)))
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
        try:
            inp = await get_input_async("")
        except EOFError:
            set_last_gid(res["gid"])
            break

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
