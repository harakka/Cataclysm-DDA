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
    result = []
    if isinstance(item, dict):
        if isObjectDefinition(item):
            # this is a type definition
            exclude_keys = {'exclude', 'exclude2'}
            item = without_keys(item, exclude_keys)
        for key in item:
            # if key != "id" and key != "type":
            #     if "type" not in item:
            #         print(f"key was {key}")
            result.extend(getValuesRecursively(item[key]))
            # if key "id" and "type" in item:
    elif isinstance(item, list):
        for listitem in item:
            result.extend(getValuesRecursively(listitem))
    else:
        result.append(item)
    return result

# dataDirs = ["core","json", "mods"]
dataDirs = ["core","json"]
argparser = ArgumentParser()
argparser.add_argument("jsondir", help="Directory that contains the json files you want to analyze")
args = argparser.parse_args()
jsonFiles = []
if not isdir(args.jsondir):
    print("Error: " + args.jsondir + " is not a folder")
    exit(1)

basedir = Path(args.jsondir)

print(str(dataDirs))

time_start = default_timer()
for subDir in dataDirs: 
    for p, d, f in walk(Path(join(args.jsondir, subDir))):
            for sourceFile in f:
                if sourceFile.endswith('.json'):
                    jsonFiles.append(join(p, sourceFile))

print(f"Find files: {default_timer() - time_start}s, {len(jsonFiles)} json source files")


time_start = default_timer()
jsonIds = []
for jsonFile in jsonFiles:
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
                        jsonIds.append((subItem, itemType, jsonFile))
                else:
                    jsonIds.append((item["id"], itemType, jsonFile))
print(f"Find ids: {default_timer() - time_start}s, {len(jsonIds)} ids")

time_start = default_timer()
jsonValues = []
for jsonFile in jsonFiles:
    with open(jsonFile) as jsonDataSource:
        data = json.load(jsonDataSource)
        flatData = getValuesRecursively(data)
        # print("flattened " + jsonFile + ", " + str(len(flatData)) + " entries")
        jsonValues = jsonValues + flatData
print(f"Find values: {default_timer() - time_start}s, {len(jsonValues)} values")

# time_start = default_timer()
# i = 0
# idsWithoutMatch = []
# for jsonId, jsonType, sourceFile in jsonIds:
#     # print(str(i) + "/" + str(len(jsonIds)) + " " + jsonId + " in " + sourceFile)

#     if jsonId not in jsonValues:
#         idsWithoutMatch.append((jsonId, jsonType, sourceFile))
#     i += 1
# # for id, type, file in idsWithoutMatch:
# #     print(id + ";" + type + ";" + file)
# print(f"Crossreference: {default_timer() - time_start}s")
