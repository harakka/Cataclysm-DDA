import json
from pathlib import Path
from os import walk
from os.path import isdir, join
from argparse import ArgumentParser
from time import sleep

def getValuesRecursively(item):
    result = []
    if isinstance(item, dict):
        for key in item:
            if key != "id":
                result.extend(getValuesRecursively(item[key]))
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

for subDir in dataDirs: 
    for p, d, f in walk(Path(join(args.jsondir, subDir))):
            for sourceFile in f:
                if sourceFile.endswith('.json'):
                    jsonFiles.append(join(p, sourceFile))

jsonIds = []
for jsonFile in jsonFiles:
    with open(jsonFile) as jsonDataSource:
        data = json.load(jsonDataSource)
        itemsToProcess = data if isinstance(data, list) else [data]
        if not isinstance(itemsToProcess, list):
            print("mitä vittua")
            raise Exception("hnngh")
        for item in itemsToProcess:
            itemType = None
            if "type" in item:
                itemType = item["type"]
            if "id" in item:
                if isinstance(item["id"], list):
                    for subItem in item["id"]:
                        jsonIds.append((subItem, itemType, jsonFile))
                else:
                    jsonIds.append((item["id"], itemType, jsonFile))
                    
jsonValues = []
for jsonFile in jsonFiles:
    with open(jsonFile) as jsonDataSource:
        data = json.load(jsonDataSource)
        flatData = getValuesRecursively(data)
        # print("flattened " + jsonFile + ", " + str(len(flatData)) + " entries")
        jsonValues = jsonValues + flatData

i = 0
idsWithoutMatch = []
for jsonId, jsonType, sourceFile in jsonIds:
    # print(str(i) + "/" + str(len(jsonIds)) + " " + jsonId + " in " + sourceFile)

    if jsonId not in jsonValues:
        idsWithoutMatch.append((jsonId, jsonType, sourceFile))
    i += 1
for id, type, file in idsWithoutMatch:
    print(id + ";" + type + ";" + file)
