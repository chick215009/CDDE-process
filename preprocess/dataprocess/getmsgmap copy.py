import os
import json
import re

#piecenum = 10000

reposet = set()
hashdict = dict()
suffixdic = dict()

filenamedic = dict()

cnt = 0
pieces = 0

foldname = r"./download-89411"

for root, dirs, files in os.walk(foldname):
    for f in dirs:
        lst = os.path.join(root,f).split("\\")
        if len(lst) == 4:
            nowfoldname = os.path.join(root,f)
            cnt += 1
            reponame = "/".join(lst[2:3:])
            #reponame= lst[2]
            hashcode = lst[3]
            for r1,d1,f1 in os.walk(nowfoldname):
                for p in f1:
                    if "A@" in p:
                        if reponame not in filenamedic:
                            filenamedic[reponame] = dict()
                        if hashcode not in filenamedic[reponame]:
                            filenamedic[reponame][hashcode] = []
                        filenamedic[reponame][hashcode].append(p[2::])
                        


with open(foldname+"_fileNameDict.json","w") as fp:
    json.dump(filenamedic,fp)
    fp.write("\n")