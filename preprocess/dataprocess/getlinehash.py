import difflib
import os
import re
import json

foldname = r"./download-89411"
diclinename = "./dicline.json"
deplicatename = "./deplicate.json"


linedic = json.load(open(diclinename,"r"))
deplicatedic = json.load(open(deplicatename,"r"))
linedicrough = json.load(open("./diclinerough.json","r"))
deplicatedicrough = json.load(open("./deplicaterough.json","r"))

outputdic = dict()
deplicateoutputdic = dict()
caselen = 90661
vis = [0 for x in range(caselen)]

def processMsg(inputmsg):
    pattern = re.compile(r'\w+')
    
    msg = pattern.findall(inputmsg)
    msg = [j for j in msg if j != '' and not j.isspace()]
    return "".join(msg)

def fixLine(difflst):
    flag = False
    for i in range(len(difflst)):
        if i % 2 == 1 and difflst[i] != '\n':
            flag = True
    
    if flag == True:
        return difflst
    else:
        return difflst[::2]

for root, dirs, files in os.walk(foldname):
    for f in dirs:
        nowfoldname = os.path.join(root,f)
        lst = os.path.join(root,f).split("\\")
        if len(lst) == 4:
            reponame = "/".join(lst[2:3:])
            #reponame= lst[2]
            hashcode = lst[3]
            f1name = ""
            f2name = ""
            retdict = dict()
            strdiff = ""
            msg = ""

            outputlst = [reponame,hashcode]

            if hashcode == "9ea62da7310ade249c9e39f5a896a466e250acf9":
                print(111)

            with open(nowfoldname + "/realMsg.txt","r",encoding="utf-8") as fp:
                msg = processMsg(fp.read())

            for r1,d1,f1 in os.walk(nowfoldname):
                for p in f1:
                    if "A@" in p:
                        f1name = os.path.join(nowfoldname,p)
                        f2name = os.path.join(nowfoldname,'B' + p[1::])    

                        filestr = p[2::]

                        with open(f1name,"r",encoding="utf-8") as beforefile, open(f2name,"r",encoding="utf-8") as afterfile:
                            beforelst = fixLine(beforefile.readlines())
                            afterlst = fixLine(afterfile.readlines())

                            lst = list(difflib.unified_diff(beforelst,afterlst))
                            strdiff = "".join(lst)
                            pos1 = strdiff.find(r"@@")
                            pos2 = pos1 + 2 + strdiff[pos1+2::].find(r"@@") 
                            atmark = strdiff[pos1:pos2 + 2:]

                        nowkeystr = filestr+msg+atmark
                        nowkeystrrough = filestr+msg

                        if nowkeystr in deplicatedic:
                            deplicateoutputdic[reponame + " " + hashcode] = nowkeystr
                            for i in deplicatedic[nowkeystr]:
                                vis[i] = 1
                            break

                        if (nowkeystrrough not in deplicatedicrough) and (nowkeystrrough in linedicrough):
                            if vis[linedicrough[nowkeystrrough]] != 0:
                                print("deplicate error!",outputlst,nowkeystrrough)
                            vis[linedicrough[nowkeystrrough]] = 1
                            if reponame not in outputdic:
                                outputdic[reponame] = dict()
                            outputdic[reponame][hashcode] = linedicrough[nowkeystrrough]
                            break

                        if nowkeystr in linedic:
                            if vis[linedic[nowkeystr]] != 0:
                                print("deplicate error!",outputlst,nowkeystr)
                            vis[linedic[nowkeystr]] = 1
                            if reponame not in outputdic:
                                outputdic[reponame] = dict()
                            outputdic[reponame][hashcode] = linedic[nowkeystr]
                            break
            if f1name == "" or f2name == "":
                print(nowfoldname)
                continue

# with open("line2hash.json","w") as fp:
#     json.dump(outputdic,fp)

with open("hash2line.json","w") as fp:
    json.dump(outputdic,fp)

with open("deplicatehash.json","w") as fp:
    json.dump(deplicateoutputdic,fp)

miscnt = 0
for i in range(caselen):
    if vis[i] != 1:
        miscnt += 1
        print(i,end=" ")
print()

print(miscnt)