import json
from . import ratings_calc
from . import thumbfetch
from . import ehutils


def url_from_entry(v):
    gid = v["gid"]
    token  = v["token"]
    return f"https://exhentai.org/g/{gid}/{token}"


async def print_entry(entry) :

    v = entry
    gid = v["gid"]
    title = v["title"]
    rating = v["rating"]
    expunged = v["expunged"]
    category = v["category"]
    tags = v["tags"]
    tags_ns = ehutils.namespace_tags(tags)
    thumb = v["thumb"]
    pages = v["filecount"]
    min_n_ratings = ratings_calc.get_least_steps(float(rating))
    print(title)
    print(url_from_entry(entry))
    for k, v in tags_ns.items():
        tag_str = k + ": "
        for vv in v:
            tag_str += vv + ", "
        tag_str = tag_str[:-2]
        print(tag_str)
    print(category)
    print(f"pages: {pages}")
    await thumbfetch.print_image(gid, thumb)
    

async def prefetch_entry(entry):
    v = entry
    gid = v["gid"]
    thumb = v["thumb"]
    #print(f"start {gid} - {thumb}")
    await thumbfetch._lookup_or_fetch(gid, thumb)
    #print(f"finish {gid} - {thumb}")
    return entry
    
