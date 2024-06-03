import os
import json

foldpath = "./output15"
outputfoldpath = "./fixedoutput14"
noneJavaWords = "Here are some none java files diff"

errordict = dict()


def processFile(root,filename):
    path = os.path.join(root, filename)
    f = open(path,"r",encoding = "UTF-8")
    print(path)
    flst = f.readlines()
    f.close()

    hashcodemap = dict()

    for i in range(len(flst)):
        if noneJavaWords in flst[i]:
            continue

        CSlst = flst[i].rstrip().split()
        
        if "处理异常" in flst[i] or "输出超长" in flst[i]:
            if ("o" + CSlst[0]) not in errordict:
                errordict["o" + CSlst[0]] = []
            errordict["o" + CSlst[0]].append(CSlst[1])       

        if len(CSlst) < 2:
            continue

        hashcodemap[CSlst[1]] = flst[i]

    w = open(os.path.join(outputfoldpath,filename),"w",encoding="UTF-8")

    for i in list(hashcodemap.values()):
        w.write(i)


    





for root, dirs, files in os.walk(foldpath):
    for f in files:
        if f.endswith(".txt"):
            processFile(root,f)


with open("errorrepo2hash14.json","w") as fp:
    json.dump(errordict,fp)
    fp.write("\n")