import json

difftextlst = json.load(open("difftextV12.json","r"))
msglst = json.load(open("msgV12.json","r"))

dicdep = {}
dic = dict()
dicrough = dict()
dicdeprough = {}
cnt = 0
print(len(difftextlst))
for i in range(len(difftextlst)):

    lst = difftextlst[i].split()
    filename = lst[3][lst[3].rfind("/")+1::]

    msg = "".join(msglst[i])
    pos1 = difftextlst[i].find(r"@@")
    pos2 = pos1 + 2 + difftextlst[i][pos1+2::].find(r"@@") 
    atmark = difftextlst[i][pos1:pos2 + 2:]

    #print(pos1,pos2,atmark)

    strdicrough = filename+msg
    strdic = filename+msg+atmark
    
    if strdic in dic:
        cnt += 1
        dicdep[strdic] = [i,dic[strdic]]
    else:
        dic[strdic] = i

    if strdicrough in dicrough:
        dicdeprough[strdicrough] = [i,dicrough[strdicrough]]
    else:
        dicrough[strdicrough] = i

print(cnt)

with open("dicline.json","w") as fp:
    json.dump(dic,fp)

with open("diclinerough.json","w") as fp:
    json.dump(dicrough,fp)

with open("deplicate.json","w") as fp:
    json.dump(dicdep,fp)

with open("deplicaterough.json","w") as fp:
    json.dump(dicdeprough,fp)
