


ALL_NAMESPACES = {
    #idk what the alias of those are 
    "temp" : "temp",
    "" : "temp",
    "r" : "reclass",
    "l" : "language",
    "lang" : "language",
    "p" : "parody",
    "series" : "parody",
    "c" : "character",
    "char" : "character",
    "g" : "group",
    "circle" : "group",
    "a" : "artist",
    "cos" : "cosplayer",
    "m" : "male",
    "f" : "female",
    "x" : "mixed",
    "o" : "other"
}

for v in set(ALL_NAMESPACES.values()):
    ALL_NAMESPACES[v] = v

def namespace_tags(tags) -> dict:
    res = {}
    for t in tags:
        if ":" in t:
            ns, value = t.split(":")
        else:
            ns = "unknown"
            value = t
        if not ns in res.keys():
            res[ns] = []
        res[ns].append(value)
    return res