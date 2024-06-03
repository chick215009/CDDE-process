import json
import re

def splt(matched):
    return " " + matched.group() + " "

def split_camel_case(text):
    """将驼峰式命名的字符串分解为单词列表。
    
    参数:
    text -- 需要分解的驼峰式命名字符串。
    
    返回:
    单词列表。
    """
    if "_" in text:
        return text.split("_")
    words = []
    word = ""
    for i, letter in enumerate(text):
        if letter.isupper() and i != 0:
            words.append(word)
            word = letter.lower()
        else:
            word += letter.lower()
    words.append(word)
    return words

def is_camel_case(s):
    return s != s.lower() and s != s.upper()

methodNamef = open(r"F:\codisumCSoutput\MethodName9.json","r")
methodNamedct = json.load(methodNamef)

classNamef = open(r"F:\codisumCSoutput\ClassName9.json","r")
classNamedct = json.load(classNamef)

fieldNamef = open(r"F:\codisumCSoutput\FieldName9.json","r")
fieldNamedct = json.load(fieldNamef)

origindiffdct = json.load(open("codisumdiff.json","r"))

msgf = open("download-89411_msg.json","r")
repomsgdct = json.load(msgf)

methodhit = 0
classhit = 0
fieldhit = 0
methodparahit = 0
fieldtypehit = 0

submethodhit = 0
subclasshit = 0
subfieldhit = 0
submethodparahit = 0
subfieldtypehit = 0

totalcase = 0

methodhitDiff = 0
classhitDiff = 0
fieldhitDiff = 0
otherhitDiff = 0
methodparahitDiff = 0
fieldtypehitDiff = 0


submethodhitDiff = 0
subclasshitDiff = 0
subfieldhitDiff = 0
subotherhitDiff = 0
submethodparahitDiff = 0
subfieldtypehitDiff = 0

misscnt = 0

orimethodlen = 0
oriclasslen = 0
orifieldlen = 0
diffmethodlen = 0
diffclasslen = 0
difffieldlen = 0
diffotherlen = 0
diffparalen = 0
difftypelen = 0

hasOOVcnt = 0
hassubOOVcnt = 0
hasDiffOOVcnt = 0
hasDiffsubOOVcnt = 0

worddict = dict()

for reponame,dic in repomsgdct.items():
    if reponame in methodNamedct:
        for hashcode,msg in dic.items():
            if hashcode in methodNamedct[reponame]:
                totalcase += 1
                checklst = [t.lower() for t in msg.split()]

                methodNameLst = set(methodNamedct[reponame][hashcode])
                classNameLst = set(classNamedct[reponame][hashcode])
                fieldNameLst = set(fieldNamedct[reponame][hashcode])

                orimethodlen += len(methodNameLst)
                oriclasslen += len(classNameLst)
                orifieldlen += len(fieldNameLst)


                diff = origindiffdct.get(reponame,dict()).get(hashcode,"")
                if diff == "":
                    misscnt += 1
                lines = diff.split("\n")
                methodLst = set()
                classLst = set()
                otherLst = set()
                fieldLst = set()
                paraLst = set()
                typeLst = set()
                checkMethodLst = set()
                checkFieldLst = set()
                checkClassLst = set()
                methodparaLst = set()
                fieldtypeLst = set()

                hasOOV = False
                hassubOOV = False
                hasDiffOOV = False
                hasDiffsubOOV = False

                for j in methodNameLst:
                    sp = (j[j.index("(") + 1:-1:]).split(",")
                    for tp in sp:
                        if tp != "":
                            methodparaLst.add(tp.lower())

                for j in fieldNameLst:
                    fieldtypeLst.add(j[j.index(":") + 2::].lower())

                optcaseClass = set()
                optcaseClassDiff = set()


                for j in methodNameLst:
                    j = j[:j.index("("):]
                    checkMethodLst.add(j.lower())
                    if j.lower() in checklst:
                        methodhit += 1
                        hasOOV = True
                    for p in split_camel_case(j):
                        if p.lower() in checklst:
                            submethodhit += 1
                            hassubOOV = True

                for j in classNameLst:
                    checkClassLst.add(j.lower())
                    if j.lower() in checklst:
                        classhit += 1
                        optcaseClass.add(j)
                        hasOOV = True
                    for p in split_camel_case(j):
                        if p.lower() in checklst:
                            subclasshit += 1
                            hassubOOV = True

                for j in fieldNameLst:
                    j = j[:j.index(":") - 1:]
                    checkFieldLst.add(j.lower())
                    if j.lower() in checklst:
                        fieldhit += 1
                        hasOOV = True
                    for p in split_camel_case(j):
                        if p.lower() in checklst:
                            subfieldhit += 1
                            hassubOOV = True

                for j in methodparaLst:
                    #paraLst.add(j.lower())
                    if j.lower() not in checkMethodLst and j.lower() not in checkFieldLst and j.lower() in checklst:
                        methodparahit += 1
                        hasOOV = True
                    for k in (re.sub(r"\W",splt,j)).split():
                        for p in split_camel_case(k):
                            if p.lower() in checklst:
                                submethodparahit += 1
                                hassubOOV = True

                for j in fieldtypeLst:
                    #typeLst.add(j.lower())
                    if j.lower() not in checkMethodLst and j.lower() not in checkFieldLst and j.lower() in checklst:
                        fieldtypehit += 1
                        hasOOV = True
                    for p in split_camel_case(j):
                        if p.lower() in checklst:
                            subfieldtypehit += 1
                            hassubOOV = True

                
                for i in lines:
                    if len(i) <= 1:
                        continue
                    # if "diff --git" in i or "@@ -" in i or "---" in i or "+++" in i:
                    #     continue
                    if i[0] == "+" or i[0] == "-":
                    # if True:
                        lstp = (re.sub(r"\W",splt,i)).split()
                        for j in lstp:
                            jlow = j.lower()
                            if (is_camel_case(j)):
                                if jlow in checkMethodLst:
                                    methodLst.add(j)
                                if jlow in checkClassLst:
                                    classLst.add(j)
                                if jlow in checkFieldLst:
                                    fieldLst.add(j)
                                if jlow not in checkMethodLst and jlow not in checkFieldLst and jlow in methodparaLst:
                                    paraLst.add(j)
                                if jlow not in checkMethodLst and jlow not in checkFieldLst and jlow in fieldtypeLst:
                                    typeLst.add(j)
                                if (jlow not in checkMethodLst) and (jlow not in checkClassLst) and (jlow not in checkFieldLst):
                                    otherLst.add(j)

                diffmethodlen += len(methodLst)
                diffclasslen += len(classLst)
                difffieldlen += len(fieldLst)
                diffparalen += len(paraLst)
                difftypelen += len(typeLst)
                diffotherlen += len(otherLst)

                calp = False

                for j in methodLst:
                    if j.lower() in checklst:
                        methodhitDiff += 1
                        
                        hasDiffOOV = True
                    for p in split_camel_case(j):
                        if p.lower() in checklst:
                            submethodhitDiff += 1
                            hasDiffsubOOV = True

                for j in classLst:
                    if j.lower() in checklst:
                        classhitDiff += 1
                        optcaseClassDiff.add(j)
                        calp = True
                        hasDiffOOV = True
                    for p in split_camel_case(j):
                        if p.lower() in checklst:
                            subclasshitDiff += 1
                            hasDiffsubOOV = True

                for j in fieldLst:
                    if j.lower() in checklst:
                        fieldhitDiff += 1
                        hasDiffOOV = True
                    for p in split_camel_case(j):
                        if p.lower() in checklst:
                            subfieldhitDiff += 1
                            hasDiffsubOOV = True
                
                for j in otherLst:
                    if j.lower() in checklst:
                        otherhitDiff += 1
                    for p in split_camel_case(j):
                        if p.lower() in checklst:
                            subotherhitDiff += 1

                for j in paraLst:
                    if j.lower() not in checkMethodLst and j.lower() not in checkFieldLst and j.lower() in checklst:
                        methodparahitDiff += 1
                        calp = True
                        hasDiffOOV = True
                    for k in (re.sub(r"\W",splt,j)).split():
                        for p in split_camel_case(k):
                            if p.lower() in checklst:
                                submethodparahitDiff += 1
                                hasDiffsubOOV = True

                for j in typeLst:
                    if j.lower() not in checkMethodLst and j.lower() not in checkFieldLst and j.lower() in checklst:
                        fieldtypehitDiff += 1
                        hasDiffOOV = True
                    for p in split_camel_case(j):
                        if p.lower() in checklst:
                            subfieldtypehitDiff += 1
                            hasDiffsubOOV = True

                if hasOOV:
                    hasOOVcnt += 1
                if hassubOOV:
                    hassubOOVcnt += 1
                if hasDiffOOV:
                    hasDiffOOVcnt += 1
                if hasDiffsubOOV:
                    hasDiffsubOOVcnt += 1




                if calp:
                    for j in checklst:
                        worddict[j] = worddict.get(j,0) + 1
                # if optcaseClass != optcaseClassDiff:
                #     print(optcaseClass,optcaseClassDiff)


print(methodhit,classhit,fieldhit)
print(submethodhit,subclasshit,subfieldhit)
print(totalcase)

print()

print(methodhitDiff,classhitDiff,fieldhitDiff,otherhitDiff)
print(submethodhitDiff,subclasshitDiff,subfieldhitDiff,subotherhitDiff)
print(misscnt)

print()

print(orimethodlen,oriclasslen,orifieldlen)
print(diffmethodlen,diffclasslen,difffieldlen,diffotherlen)

print()
print(methodparahit,fieldtypehit)
print(submethodparahit,subfieldtypehit)

print()
print(methodparahitDiff,fieldtypehitDiff)
print(submethodparahitDiff,subfieldtypehitDiff)

sorted_dict = sorted(list(worddict.items()), key=lambda item: item[1],reverse=True)

print(hasOOVcnt,hassubOOVcnt,hasDiffOOVcnt,hasDiffsubOOVcnt)

print(len(worddict))
json.dump(sorted_dict,open("wordfrequenceclass.json","w"))