import os
import json

foldpath = "./fixedoutput14"
errorpath = "./fixedoutput7"
outputfoldpath = "./fixedoutput15"
noneJavaWords = "Here are some none java files diff"
cnt = 0

errordict = dict()


def processFile(root,filename):
    global cnt
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
            continue     

        if len(CSlst) < 2:
            continue

        hashcodemap[CSlst[1]] = flst[i]

    erroroutputpath = os.path.join(errorpath,filename)

    if os.path.exists(erroroutputpath):
        fp = open(erroroutputpath,"r",encoding = "UTF-8")
        print(erroroutputpath)
        flstp = fp.readlines()
        fp.close()
        for i in range(len(flstp)):
            if noneJavaWords in flstp[i]:
                continue

            CSlst = flstp[i].rstrip().split()
            
            if "处理异常" in flstp[i] or "输出超长" in flstp[i]:
                continue     

            if len(CSlst) < 2:
                continue

#            if CSlst[1] not in hashcodemap or (hashcodemap[CSlst[1]] != flstp[i] and len(hashcodemap[CSlst[1]]) < len(flstp[i])):
            if CSlst[1] not in hashcodemap:
                cnt += 1
                hashcodemap[CSlst[1]] = flstp[i]

            #hashcodemap[CSlst[1]] = flstp[i]

    w = open(os.path.join(outputfoldpath,filename),"w",encoding="UTF-8")

    for i in list(hashcodemap.values()):
        w.write(i)


    





for root, dirs, files in os.walk(foldpath):
    for f in files:
        processFile(root,f)


print(cnt)