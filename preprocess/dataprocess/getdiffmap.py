import os
import json
import difflib

#piecenum = 10000

reposet = set()
diffdict = dict()
cnt = 0
pieces = 0

filelen = 0
maxlen = 0
cntf = 0

foldname = r"./download-89411"

for root, dirs, files in os.walk(foldname):
    for f in dirs:
        nowfoldname = os.path.join(root,f)
        lst = os.path.join(root,f).split("\\")
        if len(lst) == 4:

            cnt += 1
            reponame = "/".join(lst[2:3:])
            #reponame= lst[2]
            hashcode = lst[3]


            f1name = ""
            f2name = ""
            dflst = []
            for r1,d1,f1 in os.walk(nowfoldname):
                for p in f1:
                    if "A@" in p:
                        f1name = os.path.join(nowfoldname,p)
                        f2name = os.path.join(nowfoldname,'B' + p[1::])
                        with open(f1name,"r",encoding="utf-8") as beforefile, open(f2name,"r",encoding="utf-8") as afterfile:
                            alen = len(beforefile.read().split())
                            blen = len(afterfile.read().split())
                            maxlen = max(alen,maxlen)
                            maxlen = max(blen,maxlen)
                            cntf += 1
                            filelen += alen
                            filelen += blen

                            dflst = dflst + list(difflib.unified_diff(beforefile.readlines(),afterfile.readlines(),f1name,f2name))
            
            if f1name == "" or f2name == "":
                print(reponame,hashcode)
                continue

            if reponame not in diffdict:
                diffdict[reponame] = dict()
            diffdict[reponame][hashcode] = "".join(dflst)


print(filelen,cntf,filelen / cntf,maxlen)

# with open(foldname+"_repodownload.bat","w") as fp:
#     for i in reposet:
#         fp.write("git clone git@github.com:" + i + ".git\n")

# with open(foldname+"_diff2.json","w") as fp:
#     json.dump(diffdict,fp)
#     fp.write("\n")