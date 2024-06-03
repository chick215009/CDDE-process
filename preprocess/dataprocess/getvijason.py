import difflib
import os
import re
import json

foldname = r"./download-89411"

lssssst = []

def splt(matched):
    return " " + matched.group() + " "

def compare_files(f1,f2,msg):

    retdict = dict()


    with open(f1,"r",encoding="utf-8") as beforefile, open(f2,"r",encoding="utf-8") as afterfile:
        lst = list(difflib.unified_diff(beforefile.readlines(),afterfile.readlines(),f1,f2))
        retdict["diffs"] = "diff --git" + "".join(lst)
    
    with open(msg,"r",encoding="utf-8") as fp:
        retdict["msgs"] = fp.read()


    return retdict


for root, dirs, files in os.walk(foldname):
    for f in dirs:
        nowfoldname = os.path.join(root,f)
        lst = os.path.join(root,f).split("\\")
        if len(lst) == 4:
            f1name = ""
            f2name = ""
            retdict = dict()
            strdiff = ""
            for r1,d1,f1 in os.walk(nowfoldname):
                for p in f1:
                    if "A@" in p:
                        f1name = os.path.join(nowfoldname,p)
                        f2name = os.path.join(nowfoldname,'B' + p[1::])    

                        with open(f1name,"r",encoding="utf-8") as beforefile, open(f2name,"r",encoding="utf-8") as afterfile:
                            lst = list(difflib.unified_diff(beforefile.readlines(),afterfile.readlines(),f1name,f2name))
                            strdiff = strdiff + "".join(lst)
            
            if f1name == "" or f2name == "":
                print(nowfoldname)
                continue

            with open(nowfoldname + "/realMsg.txt","r",encoding="utf-8") as fp:
                retdict["msgs"] = fp.read()

            retdict["diffs"] = strdiff

            lssssst.append(retdict)


with open("89411_fmpp.json","w") as fp:
    json.dump(lssssst,fp)