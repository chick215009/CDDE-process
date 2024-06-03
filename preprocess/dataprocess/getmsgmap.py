import os
import json
import re

#piecenum = 10000

reposet = set()
hashdict = dict()
cnt = 0
pieces = 0

foldname = r"./download-89411"

def processMsg(inputmsg):
    pattern = re.compile(r'\w+')
    
    msg = pattern.findall(inputmsg)
    msg = [j for j in msg if j != '' and not j.isspace()]
    return " ".join(msg)

for root, dirs, files in os.walk(foldname):
    for f in dirs:
        lst = os.path.join(root,f).split("\\")
        if len(lst) == 4:
            cnt += 1
            reponame = "/".join(lst[2:3:])
            #reponame= lst[2]
            hashcode = lst[3]

            with open(os.path.join(root,f,"realMsg.txt"),"r") as ppf:
                strs = ppf.read()
                reposet.add(reponame)
                if reponame not in hashdict:
                    hashdict[reponame] = dict()
                hashdict[reponame][hashcode] = processMsg(strs)


# with open(foldname+"_repodownload.bat","w") as fp:
#     for i in reposet:
#         fp.write("git clone git@github.com:" + i + ".git\n")

with open(foldname+"_msg.json","w") as fp:
    json.dump(hashdict,fp)
    fp.write("\n")