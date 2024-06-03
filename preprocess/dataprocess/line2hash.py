import json

hash2linedict = json.load(open("cs\input\hash2line.json","r"))
line2hash = dict()

for key,value in hash2linedict.items():
    for key2,value2 in value.items():
        line2hash[value2] = [key,key2]

output = open("line2hash1.json","w")

json.dump(line2hash,output)