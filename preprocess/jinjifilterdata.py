import json
from operator import truediv
import os
from platform import java_ver
import random
import re
from tabnanny import check

validpct = 3
testpct = 3
trainpct = 14
pctsum = 20
vocrate = 0.90 #词汇摘出率
#case_name_diff = "newMCMDPtrDiff"
#case_name_CS = "newMCMDPtrCS"
#case_name_mcmdCommitBertDiff = "./mcmdCommitBertDifffixoutput/"
case_name_mcmdCodeBertDiff = "./mcmdDIFFPTRNEWFFiraN15/"
case_name_mcmdCBCS = "./mcmdCBCSPTRFFiraN15/"

CSmaxlen = 256
Ptrmaxlen = 200
msgmaxlen = 30

InputLowercase = False

alterFoldPath = r"./outputfix/"
foldpath = r"./fixedoutput15/"
#msgpath = r"D:/NJU积累/filtered_data/java/sort_random_train80_valid10_test10/"
lemmadic = {"added": "add", "fixed": "fix", "removed": "remove", "adding": "add", "fixing": "fix", "removing": "remove"}
nonJavaFileLst = ["Here", "are", "some", "none", "java", "files"]
nonJavaFileStr = "Here are some none java files"
filterFileSuffix = [". html",". xml",". gradle",". py",". md"]
typereplace = {"Ty10":"SMALL MODIFIER","Ty11":"UNKNOWN MODIFIER","Ty0":"STRUCTURE MODIFIER","Ty1":"STATE ACCESS MODIFIER","Ty2":"STATE UPDATE MODIFIER","Ty3":"BEHAVIOR MODIFIER","Ty4":"OBJECT CREATION MODIFIER","Ty5":"RELATIONSHIP MODIFIER","Ty6":"CONTROL MODIFIER","Ty7":"LARGE MODIFIER","Ty8":"LAZY MODIFIER","Ty9":"DEGENERATE MODIFIER"}

repomsgdct = dict()
repodiffdct = dict()
fileNamedct = dict()
methodNamedct = dict()
classNamedct = dict()
repoAuthordct = dict()
origindiffdct = dict()
fieldNamedct = dict()
effortcnt = 0

trainNNGDiff = []
trainNNGMSG = []
validNNGDiff = []
validNNGMSG = []
testNNGDiff = []
testNNGMSG = []

trainCSlst = []
validCSlst = []
testCSlst = []

trainDifflst = []
validDifflst = []
testDifflst = []

trainCodeBertDifflst = []
validCodeBertDifflst = []
testCodeBertDifflst = []

source_CS_vocabdic = dict()
source_CS_freq_count = 0
source_Diff_vocabdic = dict()
source_Diff_freq_count = 0
target_vocabdic = dict()
target_freq_count = 0

sourceCSPairLst = []
validCSPairLst = []
testCSPairLst = []
sourceDiffPairLst = []
validDiffPairLst = []
testDiffPairLst = []
nonoutputcnt = 0

hash2linedic = dict()
trainlinelst = []
validlinelst = []
testlinelst = []
cntpp = 0
cntlinenotfound = 0
vislst = set()
overlencnt = 0

CommitStereotype = ([("This is a structure modifier commit: this change set is composed only of setter and getter methods, and these methods perform simple access and modifications to the data. "," STRUCTUREMODIFIER "),
("This is a state access modifier commit: this change set is composed only of accessor methods, and these methods provide a client with information, but the data members are not modified. "," STATEACCESSMODIFIER "),
("This is a state update modifier commit: this change set is composed only of mutator methods, and these methods provide changes related to updates of an object's state. "," STATEUPDATEMODIFIER "),
("This is a behavior modifier commit: this change set is composed of command and non-void-command methods, and these methods execute complex internal behavioral changes within an object. "," BEHAVIORMODIFIER "),
("This is an object creation modifier commit: this change set is composed of factory, constructor, copy constructor and destructor methods, and these methods allow the creation of objects. "," OBJECTCREATIONMODIFIER "),
("This is a relationship modifier commit: this change set is composed mainly of collaborators and low number of controller methods, and these methods implement generalization, dependency and association performing calls on parameters or local variable objects. "," RELATIONSHIPMODIFIER "),
("This is a control modifier commit: this change set is composed mainly of controller, factory, constructor, copy-constructor and destructor methods, and these methods modify the external behavior of the participating classes. "," CONTROLMODIFIER "),
("This is a large modifier commit: this is a commit with many methods and combines multiple roles. "," LARGEMODIFIER "),
("This is a lazy modifier commit: this change set is composed of getter and setter methods mainly, and a low percentage of other methods. These methods denote new or planned feature that is not yet completed. "," LAZY_MODIFIER "),
("This is a degenerate modifier commit: this change set is composed of empty, incidental, and abstract methods. These methods indicate that a new feature is planned. "," DEGENERATEMODIFIER "),
("This is a small modifier commit that does not change the system significantly."," SMALLMODIFIER "),
("This is a unknown modifier commit that does not change the system significantly."," UNKNOWNMODIFIER ")])

BugFixTag = ("BUG - FEATURE: <type-ID> "," BugFix ")
StartTag = ("This change set is mainly composed of:"," CSDescribeSTART ")

def replaceTypeDescribe(strlst):
    str = " ".join(strlst)
    for i in CommitStereotype:
        str = str.replace(i[0],i[1])
    for key,value in typereplace.items():
        str = str.replace(key,value)
    str = str.replace(StartTag[0],StartTag[1])
    str = str.replace(BugFixTag[0],BugFixTag[1])
    return str

def msgLemmatization(str): #词形还原
    oristr = str
    str = str.lower()
    str = re.sub(r"\W",splt,str)
    strlst = str.split()
    for i in range(len(strlst)):
        if strlst[i] in lemmadic:
            strlst[i] = lemmadic[strlst[i]]
    return strlst

def is_camel_case(s):
    return s != s.lower() and s != s.upper() and "_" not in s
    # return s != s.lower() and "_" not in s

def split_camel_case(text):
    text = text[0].upper() + text[1::]
    return re.findall(r'[A-Z](?:[a-z]+|[A-Z]*[0-9]+)?', text)

def fixCamel(code_token,diff,methodNameLst,classNameLst,fieldNameLst):

    lines = diff.split("\n")
    fp = False
    checkMethodLst = []
    for j in methodNameLst:
        checkMethodLst.append(j[:j.index('('):])

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
    allset = set()

    for j in methodNameLst:
        sp = (j[j.index("(") + 1:-1:]).split(",")
        for tp in sp:
            if tp != "":
                methodparaLst.add(tp.lower())

    for j in fieldNameLst:
        fieldtypeLst.add(j[j.index(":") + 2::].lower())

    for j in methodNameLst:
        j = j[:j.index("("):]
        checkMethodLst.add(j.lower())


    for j in classNameLst:
        checkClassLst.add(j.lower())

    for j in fieldNameLst:
        j = j[:j.index(":") - 1:]
        checkFieldLst.add(j.lower())

    allset.update(methodparaLst)
    allset.update(fieldtypeLst)
    allset.update(checkMethodLst)
    allset.update(checkClassLst)
    allset.update(checkFieldLst)
    
    for i in lines:
        if len(i) <= 1:
            continue
        # if "download-89411" in i or "@@ -" in i:
        #     continue
        # if i[0] == "+" or i[0] == "-":
        #     lstp = (re.sub(r"\W",splt,i)).split()
        #     for j in lstp:
        #         if (is_camel_case(j) or j in checkMethodLst or j in classNameLst) and j not in code_token:
        #             if j in checkMethodLst:
        #                 methodLst.add(j)
        #             elif j in classNameLst:
        #                 classLst.add(j)
        #             else:
        #                 otherLst.add(j)
        if i[0] == "+" or i[0] == "-":
                    # if True:
            lstp = (re.sub(r"\W",splt,i)).split()
            for j in lstp:
                jlow = j.lower()
                if ((is_camel_case(j) or jlow in allset) and j not in code_token):
                    if jlow in checkMethodLst and jlow not in checkClassLst:
                        methodLst.add(j)
                    if jlow in checkClassLst:
                        classLst.add(j)
                    if jlow in checkFieldLst and jlow not in checkClassLst and jlow not in checkMethodLst:
                        fieldLst.add(j)
                    # if jlow not in checkMethodLst and jlow not in checkFieldLst and jlow in methodparaLst:
                    #     paraLst.add(j)
                    if jlow not in checkMethodLst and jlow not in checkFieldLst and jlow not in checkClassLst and jlow in fieldtypeLst:
                        typeLst.add(j)
                    if (jlow not in checkMethodLst) and (jlow not in checkClassLst) and (jlow not in checkFieldLst) and (jlow not in fieldtypeLst) and (jlow not in methodparaLst):
                        otherLst.add(j)

    if len(methodLst) != 0 or len(classLst) != 0 or len(fieldLst) != 0 or len(typeLst) != 0 or len(typeLst) != 0 or len(otherLst) != 0:
        code_token.append("Camel")
        code_token.append("Case")
        code_token.append(":")


    if len(methodLst) != 0:
        code_token.append("MethodName")
        code_token.append(":")
        for k in methodLst:
            code_token.append(k)
            code_token.extend(split_camel_case(k))
    
    if len(classLst) != 0:
        code_token.append("ClassName")
        code_token.append(":")
        for k in classLst:
            code_token.append(k)
            #code_token.extend(split_camel_case(k))

    if len(fieldLst) != 0:
        code_token.append("FieldName")
        code_token.append(":")
        for k in fieldLst:
            code_token.append(k)
    
    # if len(paraLst) != 0:
    #     code_token.append("ParaName")
    #     code_token.append(":")
    #     for k in paraLst:
    #         code_token.append(k)
    
    if len(typeLst) != 0:
        code_token.append("TypeName")
        code_token.append(":")
        for k in typeLst:
            code_token.append(k)

    if len(otherLst) != 0:
        code_token.append("Identifier")
        code_token.append(":")
        for k in otherLst:
            code_token.append(k)



    return code_token

def fixDiffCamel(code_token,diff,methodNameLst,classNameLst):

    lines = diff.split("\n")
    fp = False
    checkMethodLst = []
    for j in methodNameLst:
        checkMethodLst.append(j[:j.index('('):])

    methodLst = set()
    classLst = set()
    otherLst = set()
    
    for i in lines:
        if len(i) <= 1:
            continue
        if "download-89411" in i or "@@ -" in i:
            continue
        if i[0] == "+" or i[0] == "-":
            lstp = (re.sub(r"\W",splt,i)).split()
            for j in lstp:
                if (is_camel_case(j) or j in checkMethodLst or j in classNameLst):
                    if j in checkMethodLst:
                        methodLst.add(j)
                    elif j in classNameLst:
                        classLst.add(j)
                    else:
                        otherLst.add(j)

    if len(methodLst) != 0 or len(classLst) != 0 or len(otherLst) != 0:
        code_token.append("Camel")
        code_token.append("Word")

    if len(methodLst) != 0:
        code_token.append("MethodName")
        code_token.append(":")
        for k in methodLst:
            code_token.append(k)
    
    if len(classLst) != 0:
        code_token.append("ClassName")
        code_token.append(":")
        for k in classLst:
            code_token.append(k)

    if len(otherLst) != 0:
        code_token.append("OtherName")
        code_token.append(":")
        for k in otherLst:
            code_token.append(k)


    return code_token

def fixCodeToken(code_token):
    if isinstance(code_token,list):
        code_token = " ".join(code_token)

    code_token = re.sub(r"\W",splt,code_token)
    if InputLowercase:
        code_token = code_token.lower()

    code_token = code_token.replace("CLASS","class")
    code_token = code_token.replace("METHOD","method")
    code_token = code_token.replace("FIELD","field")
    code_token = code_token.replace("nodeChanges","node Changes")
    
    return code_token.split()


def splt(matched):
    return " " + matched.group() + " "

def getdct():
    global repomsgdct
    global repodiffdct
    global trainlinelst
    global validlinelst
    global testlinelst
    global hash2linedic
    global fileNamedct
    global methodNamedct
    global classNamedct
    global repoAuthordct
    global origindiffdct
    global fieldNamedct

    msgf = open("download-89411_msg.json","r")
    repomsgdct = json.load(msgf)

    origindiffdct = json.load(open("codisumdiff.json","r"))

    difff = open("download-89411_diff2.json","r")
    repodiffdct = json.load(difff)

    fileNamef = open("download-89411_fileNameDict.json","r")
    fileNamedct = json.load(fileNamef)

    methodNamef = open(r"F:\codisumCSoutput\MethodName.json","r")
    methodNamedct = json.load(methodNamef)

    classNamef = open(r"F:\codisumCSoutput\ClassName.json","r")
    classNamedct = json.load(classNamef)

    fieldNamef = open(r"F:\codisumCSoutput\FieldName15.json","r")
    fieldNamedct = json.load(fieldNamef)

    indexdic = json.load(open(r"FIRA-ICSE-main\all_index","r"))
    trainlinelst = indexdic["train"]
    validlinelst = indexdic["valid"]
    testlinelst = indexdic["test"]

    hash2linedic = json.load(open("hash2line.json", "r"))

    repoAuthordct = json.load(open("download-89411_author.json","r"))
    # difff = open(msgpath+prefix+".diff.txt",encoding = "utf-8")
    # msgf = open(msgpath+prefix+".msg.txt",encoding = "utf-8")
    # repof = open(msgpath+prefix+".repo.txt",encoding = "utf-8")
    # shaf = open(msgpath+prefix+".sha.txt",encoding = "utf-8")

    # difflst = difff.readlines()
    # msglst = msgf.readlines()
    # repolst = repof.readlines()
    # shalst = shaf.readlines()

    # for i in range(len(msglst)):
    #     reponame = "/" + repolst[i].rstrip().split(r"/")[1]
    #     if reponame not in repomsgdct:
    #         repomsgdct[reponame] = dict()
    #         repodiffdct[reponame] = dict()
    #     repomsgdct[reponame][shalst[i].rstrip()] = msglst[i].rstrip()
    #     repodiffdct[reponame][shalst[i].rstrip()] = difflst[i].rstrip()

    msgf.close()
    # repof.close()
    # shaf.close()

WildCard = "#$%#"

def checkTypeTheSame(tp1,tp2):
    if len(tp1) >= len(tp2):
        tp1 = tp1[:len(tp2):]
    else:
        return False

    for i in range(len(tp1)):
        if tp1[i] != tp2[i] and tp1[i] != WildCard and tp2[i] != WildCard:
            return False
    return True

def checkLstPattern(strlst):
    patternLst = [["merge", "pull", "request", "from"],["see", WildCard,WildCard,WildCard,"log"],["java","docs"],["clean","code"],["fix","typo"]]

    for lst in patternLst:
        if checkTypeTheSame(strlst,lst):
            return True
    return False


def checkNNGPattern(strlst):
    str = " ".join(strlst)
    pattern = ([r'^ignore update \' .* \.$',
    r'^update(d)? (changelog|gitignore|readme( . md| file)?)( \.)?$',
    r'^prepare version (v)?[ \d.]+$',
    r'^bump (up )?version( number| code)?( to (v)?[ \d.]+( - snapshot)?)?( \.)?$',
    r'^modify (dockerfile|makefile)( \.)?$',
    r'^update submodule(s)?( \.)?$'])
    for i in pattern:
        if re.search(i,str) != None:
            print("NNG FILTER!")
            return True
    return False

def checkmsg(msg):

    if msg == "":
        return False
    if len(msg) >= msgmaxlen:
        return False
    if len(msg) <= 1: # like update/polish
        return False
    if checkLstPattern(msg):
        return False
    if checkNNGPattern(msg):
        return False
    
    return True

def getAddAndDelToken(diff):
    lines = diff.split(" <nl> ")
    addtoken = []
    deltoken = []
    for i in lines:
        lst = i.split()
        if lst[0] == "+":
            addtoken.extend(lst[1::])
        elif lst[0] == "-":
            deltoken.extend(lst[1::])

    return " ".join(addtoken)," ".join(deltoken)

def fileFilter(diff):
    for i in filterFileSuffix:
        if i in diff:
            return True
    
    return False

def findMultipleNote(diff,CSoutput):
    CSstr = " ".join(CSoutput)
    lines = diff.split("\n")
    addLines = []
    addLine = []
    delLines = []
    delLine = []
    addAnnotation = []
    delAnnotation = []
    importpart = []
    for i in lines:
        if len(i) <= 1:
            continue
        if i[0] == "+":
            nowline = i[1::].strip()
            if nowline == "":
                continue
            if nowline[0] == "*" or nowline[:3:] == "/**" or "*/" in nowline:
                if nowline not in CSstr:
                    addLines.append(nowline)
            if nowline[:2:] == "//":
                if nowline not in CSstr:
                    if "todo" in nowline or "TODO" in nowline or "ToDo" in nowline:
                        nowline = "todo" + nowline
                    addLine.append(nowline)
            if nowline[0] == "@":
                pos = nowline.find("(")
                tp = ""
                if pos == -1:
                    tp = nowline[1::]
                else:
                    tp = nowline[1:pos:]
                if tp not in CSstr and nowline[1::] not in addAnnotation:
                    addAnnotation.append(nowline[1::])

        elif i[0] == "-":
            nowline = i[1::].strip()
            if nowline == "":
                continue
            if nowline[0] == "*" or nowline[:3:] == "/**" or "*/" in nowline:
                if nowline not in CSstr:
                    delLines.append(nowline)
            if nowline[:2:] == "//":
                if nowline not in CSstr:
                    if "todo" in nowline or "TODO" in nowline or "ToDo" in nowline:
                        nowline = "todo" + nowline
                    delLine.append(nowline)
            if nowline[0] == "@":
                pos = nowline.find("(")
                tp = ""
                if pos == -1:
                    tp = nowline[1::]
                else:
                    tp = nowline[1:pos:]
                if tp not in CSstr and nowline[1::] not in delAnnotation:
                    delAnnotation.append(nowline[1::])
        # https://github.com/bazelbuild/bazel/commit/94268c80000593d5f226595087f5cdfaab87ddbe
        # if "import" in i:
        #     if len(importpart) == 0:
        #         importpart.extend(["Import","Part"])
        #     importpart.extend(i.split())

        # if "+ *" in i or "+ / * *" in i:
        #     addLines.append(i[2::])
        # elif "- *" in i or "- / * *" in i:
        #     delLines.append(i[2::])

    addret = []
    delret = []
    if len(addLine) != 0:
        addret.extend(("Add line note: " + " Add line note: ".join(addLine)).split())
    if len(delLine) != 0:
        delret.extend(("Remove line note: " + " Remove line note: ".join(delLine)).split())
    if len(addLines) != 0:
        multiplecomment = " ".join(addLines)
        if "license" in multiplecomment or "License" in multiplecomment:
            addret.extend(("Add license multiple note: " + multiplecomment).split())
        elif len(multiplecomment.split()) > 40:
            addret.extend(("Add javadoc multiple note: " + multiplecomment).split())
        else:
            addret.extend(("Add multiple note: " + multiplecomment).split())
    if len(delLines) != 0:
        multiplecomment = " ".join(delLines)
        if "license" in multiplecomment or "License" in multiplecomment:
            delret.extend(("Remove license multiple note: " + multiplecomment).split())
        elif len(multiplecomment.split()) > 40:
            delret.extend(("Remove javadoc multiple note: " + multiplecomment).split())
        else:
            delret.extend(("Remove multiple note: " + multiplecomment).split())
    if len(addAnnotation) != 0:
        addret.extend(("Add annotation: " + " ".join(addAnnotation)).split())
    if len(delAnnotation) != 0:
        delret.extend(("Remove annotation: " + " ".join(delAnnotation)).split())
    return addret,delret,importpart

def count_uppercase_letters(s):
    return sum(1 for char in s if char.isupper())

def checkIfNoOutput(CSout):
    Mindex = CSout.find("Changes to")
    if Mindex == -1:
        if len(CSout.split()) >= 20:
            return True
        else:
            return False
    tmplst = CSout[Mindex::].split("Change in ")
    if Mindex != -1:
        tmplst = tmplst[1::]
    for i in tmplst:
        ilst = i.split()
        ilen = count_uppercase_letters(ilst[0])
        if ("for" in ilst and len(i.split()) >= 5 + count_uppercase_letters(ilst[0])) or ("for" not in ilst and len(ilst) >= 5):
            return True
        # if len(i.split()) >= 10:
        #     return True
    return False

def readAlterFile(alterpath):
    dic = dict()

    if not os.path.exists(alterpath):
        return dic
    
    print(alterpath)
    f = open(alterpath,"r",encoding = "UTF-8")
    
    flst = f.readlines()
    f.close()

    for i in range(len(flst)):
        if nonJavaFileStr in flst[i]:
            continue
        CSlst = flst[i].rstrip().split()
        if len(CSlst) <= 2:
            print(CSlst)
            continue
        if CSlst[2] == "处理异常" or CSlst[2] == "无明显变化" or CSlst[2] == "输出超长":
            continue
        if len(CSlst) >= CSmaxlen:
            continue

        dic[CSlst[1]] = flst[i]

    return dic


def defaultoutput(diff,CSoutput):
    LineLst = []

    CSstr = " ".join(CSoutput)
    CSstr = CSstr.replace("METHOD","method")
    CSstr = CSstr.replace("CLASS","class")
    CSstr = CSstr.replace("paramater","parameter")
    pos = CSstr.find(':')
    LineLst.append(CSstr[:pos + 1:])
    LineLst.extend(re.compile("Modifications to .+?java").findall(CSstr))
    LineLst.extend(re.compile("Change in .+?java").findall(CSstr))
    LineLst.extend(re.compile("empty file .+?java").findall(CSstr))

    # for i in re.compile("at [^*<>]+? method|in [^*<>]+? method|at [^*<>]+? class|in [^*<>]+? class").findall(CSstr):
    #     if len(i) > 50:
    #         print(i)


    lines = diff.split("\n")
    
    for i in lines:
        if len(i) <= 1:
            continue
        if "download-89411" in i or "@@ -" in i:
            continue
        if i[0] == "+":
            nowline = i[1::].strip()
            LineLst.append("Add line " + nowline)
        elif i[0] == "-":
            nowline = i[1::].strip()
            LineLst.append("Remove line " + nowline)
        else:
            nowline = i.strip()
            LineLst.append("Match line " + nowline)

    LineLst.extend(re.compile("at [^*<>]+? method|in [^*<>]+? method|at [^*<>]+? class|in [^*<>]+? class").findall(CSstr))
    
    return LineLst

def filterExtraFile(reponame,hashcode,CSStr):
    global effortcnt

    packageLst = CSStr.split("Changes to")

    CSpos = packageLst[0].find("ChangeScribeStart")
    if CSpos == -1:
        CSpos = 0
    outputStr = packageLst[0][:CSpos:] + "ChangeScribeStart "

    fileNameLst = fileNamedct[reponame][hashcode]
    cntFile = set()

    if CSpos != 0:
        CSpos += 18

    lstzeroAst = re.compile(".+? a almost empty file .+? with zero ast node").findall(packageLst[0][CSpos::])
    for i in lstzeroAst:
        for j in i.split():
            if ".java" in j and j in fileNameLst:
                outputStr = outputStr + i
                cntFile.add(j)
                break


    for i in packageLst[1::]:
        FileScribeLst = i.split("Change in ")
        if "Modifications to " in i:
            FileScribeLst = i.split("Modifications to ")
        Fileoutput = ""

        nowadd = True

        for j in FileScribeLst[1::]:
            Filename = j.strip().split()[0]
            if Filename.endswith(".java"):
                if Filename in fileNameLst:
                    Fileoutput = Fileoutput + " Change in " + j
                    cntFile.add(Filename)
                    nowadd = True
                else:
                    nowadd = False
            else:
                if nowadd:
                    Fileoutput = Fileoutput + " Change in " + j
        
        if Fileoutput != "":
            Fileoutput = "Changes to " + FileScribeLst[0] + Fileoutput

        outputStr = outputStr + Fileoutput

    if len(cntFile) != len(fileNameLst):
        effortcnt += 1

    # if CSStr != outputStr:
    #     effortcnt += 1

    return outputStr.split()




def processFile(root,filename):
    path = os.path.join(root, filename)
    #alterdic = readAlterFile(os.path.join(alterFoldPath,filename))
    global source_CS_freq_count
    global source_Diff_freq_count
    global target_freq_count
    global nonoutputcnt
    global cntpp
    global cntlinenotfound
    global vislst
    global overlencnt

    f = open(path,"r",encoding = "UTF-8")
    print(path)
    flst = f.readlines()

    f.close()
    random.shuffle(flst)
    cnt = 0
    filteredcnt = 0

    nonoutputfile = open("nonoutput1.csv","a",encoding = "UTF-8")

    for i in range(len(flst)):
        # if nonJavaFileStr in flst[i]: #非java文件
        #     continue

        CSlst = flst[i].rstrip().split()
        if len(CSlst) <= 2:
            print(CSlst)
            continue

        linenum = hash2linedic.get(CSlst[0][1::],dict()).get(CSlst[1],-1)
        if linenum == -1:
            print("line not found",CSlst[0],CSlst[1])
            cntlinenotfound += 1
            continue

        if linenum in vislst:
            continue
        else:
            vislst.add(linenum)
        # if CSlst[1] in alterdic:
        #     CSlst = alterdic[CSlst[1]].rstrip().split()
        #     print(CSlst[1])
        CSflag = True
        if CSlst[2] == "处理异常" or CSlst[2] == "无明显变化" or CSlst[2] == "输出超长":
            cntpp += 1
            CSflag = False

        # if CSlst[1] == "6469bffe6185dc25634dcbc38838ecc8c5784f9e":
        #     print(1)


        msg = repomsgdct.get(CSlst[0][1::],dict()).get(CSlst[1],"")
        msg = msgLemmatization(msg)
        if not checkmsg(msg):
            continue

        diff = repodiffdct.get(CSlst[0][1::],dict()).get(CSlst[1],"")
        ogdiff = origindiffdct.get(CSlst[0][1::],dict()).get(CSlst[1],"")
        #if fileFilter(diff):#过滤非java文件
        #    filteredcnt += 1
        #    continue

        # add_token,del_token = getAddAndDelToken(diff)
        filteredCSOutput = filterExtraFile(CSlst[0][1::],CSlst[1]," ".join(CSlst[2::]))
        add_mul_note,del_mul_note,import_part = findMultipleNote(diff,filteredCSOutput)
        # print(add_mul_note,del_mul_note)
        # if (len(add_mul_note) != 0 or len(del_mul_note) != 0) and CSflag == True:
        #     print("comment added!")
        rpname = CSlst[0][1::]
        tmplstCS = [rpname] + filteredCSOutput + add_mul_note + del_mul_note + import_part
        #tmplstCS = [repoAuthordct[rpname],"/", rpname] + filteredCSOutput
        # tmplstCS = filteredCSOutput + add_mul_note + del_mul_note + import_part
        # tmplstCS = CSlst[2::] + add_mul_note + del_mul_note
        CScode_token = fixCodeToken(replaceTypeDescribe(tmplstCS))

        # if (CSlst[1] == "7992ed62d349106efe19188398981c147f63b33e"):
        #     print(111)

        if not checkIfNoOutput(" ".join(CScode_token)):
            nonoutputcnt += 1
            nonoutputfile.write(CSlst[0]+","+CSlst[1]+",")
            nonoutputfile.write(" ".join(CSlst[2::]))
            nonoutputfile.write(",")
            nonoutputfile.write(repodiffdct.get(CSlst[0],dict()).get(CSlst[1],""))
            nonoutputfile.write("\n")
            CSflag = False

        # if msg == ['remove', 'unnecessary', 'condition']:
        #     print(len(ogdiff.split()),len(tmplstCS))

        if len(tmplstCS) - len(add_mul_note) - len(del_mul_note) - len(ogdiff.split()) > 50:
            # if (len(diff.split()) <= 30):
            #     print(1)
            # print(ogdiff)
            # print(" ".join(tmplstCS))
            # print(msg,len(ogdiff.split()),len(tmplstCS),rpname,CSlst[1])
            overlencnt += 1
            CSflag = False

        CScode_token = fixCamel(CScode_token,diff,methodNamedct[CSlst[0][1::]].get(CSlst[1],[]),classNamedct[CSlst[0][1::]].get(CSlst[1],[]),fieldNamedct[CSlst[0][1::]].get(CSlst[1],[]))

        if len(CScode_token) >= CSmaxlen:
            pass
            #CSflag = False
            #overlencnt += 1

        if len(diff.split()) >= CSmaxlen:
            pass
            #overlencnt += 1

        # tmpDiffdic = dict()
        # tmpDiffdic["add_tokens"] = add_token
        # tmpDiffdic["del_tokens"] = del_token
        # tmpDiffdic["commit_tokens"] = msg
        # tmpDiffdic["repo"] = CSlst[0]
        # tmpDiffdic["sha"] = CSlst[1]

        tmpCSdic = dict()
        if CSflag == True:
            tmpCSdic["code_tokens"] = CScode_token
        else:
            tmpCSdic["code_tokens"] = fixCodeToken([rpname] + defaultoutput(diff,filteredCSOutput))
            # tmpCSdic["code_tokens"] = fixCodeToken(defaultoutput(diff,filteredCSOutput))
            # tmpCSdic["code_tokens"].extend(CScode_token)
        tmpCSdic["docstring_tokens"] = msg
        tmpCSdic["repo"] = CSlst[0]
        tmpCSdic["sha"] = CSlst[1]
        tmpCSdic["fira_line"] = linenum

        tmpCBDiffdic = dict()
        tmpCBDiffdic["code_tokens"] = [rpname] + fixCodeToken(fixDiffCamel(fixCodeToken(ogdiff),diff,methodNamedct[CSlst[0][1::]].get(CSlst[1],[]),classNamedct[CSlst[0][1::]].get(CSlst[1],[])))
        tmpCBDiffdic["docstring_tokens"] = msg
        tmpCBDiffdic["repo"] = CSlst[0]
        tmpCBDiffdic["sha"] = CSlst[1]
        tmpCBDiffdic["fira_line"] = linenum

        # pairDiffStr = (diff," ".join(msg))
        # pairCSStr = (" ".join(CScode_token)," ".join(msg))

        num = cnt % pctsum

        # if num < trainpct + validpct:
        #     #if len(pairDiffStr[0].split()) < CSmaxlen: 
        #     for wod in diff.split():
        #         source_Diff_vocabdic[wod] = source_Diff_vocabdic.get(wod, 0) + 1
        #         source_Diff_freq_count += 1
        #     for wod in CScode_token:
        #         source_CS_vocabdic[wod] = source_CS_vocabdic.get(wod, 0) + 1
        #         source_CS_freq_count += 1
        #     for wod in msg:
        #         target_vocabdic[wod] = target_vocabdic.get(wod, 0) + 1
        #         target_freq_count += 1

        if linenum in trainlinelst:
            tmpCSdic["partition"] = "train"
            tmpCBDiffdic["partition"] = "train"
            # if CSflag:
            trainCSlst.append(tmpCSdic)
            trainCodeBertDifflst.append(tmpCBDiffdic)
            trainNNGDiff.append(ogdiff)
            trainNNGMSG.append(" ".join(msg))
            # trainDifflst.append(tmpDiffdic)
            # sourceCSPairLst.append(pairCSStr)
            # if len(pairDiffStr[0].split()) < Ptrmaxlen:
            #     sourceDiffPairLst.append(pairDiffStr)
        elif linenum in validlinelst:
            tmpCSdic["partition"] = "valid"
            tmpCBDiffdic["partition"] = "valid"
            # if CSflag:
            validCSlst.append(tmpCSdic)
            validCodeBertDifflst.append(tmpCBDiffdic)
            validNNGDiff.append(ogdiff)
            validNNGMSG.append(" ".join(msg))
            # validDifflst.append(tmpDiffdic)
            # validCSPairLst.append(pairCSStr)
            # if len(pairDiffStr[0].split()) < Ptrmaxlen:
            #     validDiffPairLst.append(pairDiffStr)
        elif linenum in testlinelst:
            tmpCSdic["partition"] = "test"            
            tmpCBDiffdic["partition"] = "test"
            # if CSflag:
            testCSlst.append(tmpCSdic)
            testCodeBertDifflst.append(tmpCBDiffdic)
            testNNGDiff.append(ogdiff)
            testNNGMSG.append(" ".join(msg))
            # testDifflst.append(tmpDiffdic)
            # testCSPairLst.append(pairCSStr)
            # if len(pairDiffStr[0].split()) < Ptrmaxlen:    
            #     testDiffPairLst.append(pairDiffStr)

        cnt += 1
    
    #print(filteredcnt)

def writefile(lst,path):
    with open(path,"w") as f:
        for i in lst:
            json.dump(i,f)
            f.write("\n")

def getvocabfile(case_name,vocabdic, freq_count, suffix):
    items = sorted(vocabdic.items(), key=lambda item: -item[1])

    words = list()
    cur_freq_count = 0
    for idx, (word, count) in enumerate(items):
        cur_freq_count += count
        if cur_freq_count / freq_count > vocrate:
            print('words_total', idx,"/",len(items))
            break
        words.append(word)

    writeToCaseFile(case_name,suffix,words)

def writeToCaseFile(case_name,suffix,wordsLst):
    if not os.path.exists(os.path.join(case_name)):
        os.mkdir(os.path.join(case_name))

    cfileName = os.path.join(case_name,case_name + suffix)

    opFile = open(cfileName,"wb")
    opFile.write("\n".join(wordsLst).encode("utf-8"))
    opFile.close()

def getSourceFileAndTargetFile(case_name,pairlst,suffix):
    sourcelst = [x[0] for x in pairlst]
    targetlst = [x[1] for x in pairlst]

    writeToCaseFile(case_name,suffix + ".source",sourcelst)
    writeToCaseFile(case_name,suffix + ".target",targetlst)

def main():
    random.seed(114514)
    getdct()

    nonoutputfile = open("nonoutput1.csv","w",encoding = "UTF-8")
    nonoutputfile.close()

    for root, dirs, files in os.walk(foldpath):
        for f in files:
            processFile(root,f)

    # getvocabfile(case_name_diff,source_Diff_vocabdic,source_Diff_freq_count,".vocab.source")
    # getvocabfile(case_name_diff,target_vocabdic,target_freq_count,".vocab.target")
    # getSourceFileAndTargetFile(case_name_diff,validDiffPairLst,".eval")
    # getSourceFileAndTargetFile(case_name_diff,sourceDiffPairLst,".train")
    # getSourceFileAndTargetFile(case_name_diff,testDiffPairLst,".test")

    # getvocabfile(case_name_CS,source_CS_vocabdic,source_CS_freq_count,".vocab.source")
    # getvocabfile(case_name_CS,target_vocabdic,target_freq_count,".vocab.target")
    # getSourceFileAndTargetFile(case_name_CS,validCSPairLst,".eval")
    # getSourceFileAndTargetFile(case_name_CS,sourceCSPairLst,".train")
    # getSourceFileAndTargetFile(case_name_CS,testCSPairLst,".test")

    # if not os.path.exists(case_name_mcmdCommitBertDiff):
    #    os.mkdir(case_name_mcmdCommitBertDiff)
    # writefile(trainDifflst,case_name_mcmdCommitBertDiff + "train.jsonl")
    # writefile(validDifflst,case_name_mcmdCommitBertDiff + "valid.jsonl")
    # writefile(testDifflst,case_name_mcmdCommitBertDiff + "test.jsonl")

    if not os.path.exists(case_name_mcmdCodeBertDiff):
       os.mkdir(case_name_mcmdCodeBertDiff)
    writefile(trainCodeBertDifflst,case_name_mcmdCodeBertDiff + "train.jsonl")
    writefile(validCodeBertDifflst,case_name_mcmdCodeBertDiff + "valid.jsonl")
    writefile(testCodeBertDifflst,case_name_mcmdCodeBertDiff + "test.jsonl")

    if not os.path.exists(case_name_mcmdCBCS):
       os.mkdir(case_name_mcmdCBCS)
    writefile(trainCSlst,case_name_mcmdCBCS + "train.jsonl")
    writefile(validCSlst,case_name_mcmdCBCS + "valid.jsonl")
    writefile(testCSlst,case_name_mcmdCBCS + "test.jsonl")

    writefile(trainNNGDiff,"./NNGCase/train.diff")
    writefile(trainNNGMSG,"./NNGCase/train.msg")
    writefile(validNNGDiff,"./NNGCase/valid.diff")
    writefile(validNNGMSG,"./NNGCase/valid.msg")
    writefile(testNNGDiff,"./NNGCase/test.diff")
    writefile(testNNGMSG,"./NNGCase/test.gold")


    print("CS异常：",cntpp)
    print("line not found",cntlinenotfound)
    print(nonoutputcnt)
    print(len(vislst))
    print(effortcnt)
    print(overlencnt)
    nonoutputfile.close()

main()

    