import json
from pathlib import Path
from os import walk
from os.path import isdir, join
from argparse import ArgumentParser
from time import sleep
from timeit import default_timer


def isObjectDefinition(item):
    if isinstance(item, dict) and "id" in item and "type" in item:
        return True
    return False


def without_keys(d, keys):
    return {x: d[x] for x in d if x not in keys}


def getValuesRecursively(item):
    result = set()
    if isinstance(item, dict):
        if isObjectDefinition(item):
            # this is a type definition
            exclude_keys = {"id", "type"}
            item = without_keys(item, exclude_keys)
        for key in item:
            # if key != "id" and key != "type":
            #     if "type" not in item:
            #         print(f"key was {key}")
            result.update(getValuesRecursively(item[key]))
            # if key "id" and "type" in item:
    elif isinstance(item, list):
        for listitem in item:
            result.update(getValuesRecursively(listitem))
    else:
        result.add(item)
    return result


dataDirs = ["core", "json", "mods"]
# dataDirs = ["core", "json"]
argparser = ArgumentParser()
argparser.add_argument(
    "jsondir", help="Directory that contains the json files you want to analyze"
)
# argparser.add_argument("dest", help="File to write the results into.")
args = argparser.parse_args()
jsonFiles = set()
jsonFilesMods = set()
if not isdir(args.jsondir):
    print("Error: " + args.jsondir + " is not a folder")
    exit(1)

basedir = Path(args.jsondir)

time_start = default_timer()
for subDir in dataDirs:
    for path, _, files in walk(Path(join(args.jsondir, subDir))):
        for sourceFile in files:
            fullPath = join(path, sourceFile)
            if fullPath.endswith(".json") and "obsolet" not in fullPath:
                if fullPath.startswith(join("data", "mods")):
                    jsonFilesMods.add(fullPath)
                else:
                    jsonFiles.add(fullPath)


# print(
#     f"Find files: {default_timer() - time_start}s, {len(jsonFiles)} json source files"
# )

time_start = default_timer()
jsonIds = set()
for jsonFile in jsonFiles.union(jsonFilesMods):
    with open(jsonFile) as jsonDataSource:
        data = json.load(jsonDataSource)
        itemsToProcess = data if isinstance(data, list) else [data]
        if not isinstance(itemsToProcess, list):
            print("mitä vittua")
            raise Exception("hnngh")
        for item in itemsToProcess:
            if "type" in item and "id" in item:
                itemType = item["type"]
                if isinstance(item["id"], list):
                    for subItem in item["id"]:
                        jsonIds.add((subItem, itemType, jsonFile))
                else:
                    jsonIds.add((item["id"], itemType, jsonFile))
# print(f"Find ids: {default_timer() - time_start}s, {len(jsonIds)} ids")

time_start = default_timer()
jsonValuesMods = set()
jsonValues = set()
for jsonFile in jsonFiles:
    with open(jsonFile) as jsonDataSource:
        data = json.load(jsonDataSource)
        flatData = getValuesRecursively(data)
        # print(f"flattened {jsonFile}, {flatData} entries. Data: {flatData}")
        jsonValues.update(flatData)
for jsonFile in jsonFilesMods:
    with open(jsonFile) as jsonDataSource:
        data = json.load(jsonDataSource)
        flatData = getValuesRecursively(data)
        # print(f"flattened {jsonFile}, {flatData} entries. Data: {flatData}")
        jsonValuesMods.update(flatData)
# print(f"Find values: {default_timer() - time_start}s, {len(jsonValues)} values")

time_start = default_timer()
i = 0
idsWithoutMatch = set()
idsWithMatchOnlyInMods = set()
for jsonId, jsonType, sourceFile in jsonIds:
    # print(f"Finding match for {jsonId}/{jsonType} ({sourceFile})")
    if jsonId not in jsonValues:
        idsWithoutMatch.add((jsonId, jsonType, sourceFile))
        if jsonId in jsonValuesMods:
            idsWithMatchOnlyInMods.add((jsonId, jsonType, sourceFile))
    i += 1
# print(f"Crossreference: {default_timer() - time_start}s")

print("###Ids without match in base game data")
print("id;type;file")
for id, type, file in idsWithoutMatch:
    print(id + ";" + type + ";" + file)
print("###Ids with match only in mods")
print("id;type;file")
for id, type, file in idsWithMatchOnlyInMods:
    print(id + ";" + type + ";" + file)
# TODO this doesn't work, we gather ids from mods and base game data into one set. Need to gather base game and mod ids separately and check separately
