import os
import json

authordic = dict()
cnt = 0
pieces = 0

foldname = r"./download-89411"

for root, dirs, files in os.walk(foldname):
    for f in dirs:
        lst = os.path.join(root,f).split("\\")
        if len(lst) == 3:
            authordic[lst[2]] = lst[1]

with open(foldname+"_author.json","w") as fp:
    json.dump(authordic,fp)
    fp.write("\n")