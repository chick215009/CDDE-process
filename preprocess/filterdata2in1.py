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
case_name_diff = "newMCMDPtrDiff"
case_name_CS = "newMCMDPtrCS"
case_name_mcmdCommitBertDiff = "./mcmdCommitBertDifffixoutput/"
case_name_mcmdCodeBertDiff = "./mcmdCodeBertDifffixoutput/"
case_name_mcmdCBCS = "./mcmdCBCSfixoutput/"

CSmaxlen = 100
Ptrmaxlen = 200
msgmaxlen = 30

InputLowercase = False

alterFoldPath = r"./outputfix/"
foldpath = r"./output5-2/"
msgpath = r"D:/NJU积累/filtered_data/java/sort_random_train80_valid10_test10/"
lemmadic = {"added": "add", "fixed": "fix", "removed": "remove", "adding": "add", "fixing": "fix", "removing": "remove"}
nonJavaFileLst = ["Here", "are", "some", "none", "java", "files"]
nonJavaFileStr = "Here are some none java files"
filterFileSuffix = [". html",". xml",". gradle",". py",". md"]

repomsgdct = dict()
repodiffdct = dict()

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
    str = str.replace(StartTag[0],StartTag[1])
    str = str.replace(BugFixTag[0],BugFixTag[1])
    return str

def msgLemmatization(str): #词形还原
    str = str.lower()
    str = re.sub(r"\W",splt,str)
    strlst = str.split()
    for i in range(len(strlst)):
        if strlst[i] in lemmadic:
            strlst[i] = lemmadic[strlst[i]]
    return strlst

def fixCodeToken(code_token):
    if isinstance(code_token,list):
        code_token = " ".join(code_token)

    code_token = re.sub(r"\W",splt,code_token)
    if InputLowercase:
        code_token = code_token.lower()
    
    return code_token.split()


def splt(matched):
    return " " + matched.group() + " "

def getdct(prefix):
    difff = open(msgpath+prefix+".diff.txt",encoding = "utf-8")
    msgf = open(msgpath+prefix+".msg.txt",encoding = "utf-8")
    repof = open(msgpath+prefix+".repo.txt",encoding = "utf-8")
    shaf = open(msgpath+prefix+".sha.txt",encoding = "utf-8")

    difflst = difff.readlines()
    msglst = msgf.readlines()
    repolst = repof.readlines()
    shalst = shaf.readlines()

    for i in range(len(msglst)):
        reponame = "/" + repolst[i].rstrip().split(r"/")[1]
        if reponame not in repomsgdct:
            repomsgdct[reponame] = dict()
            repodiffdct[reponame] = dict()
        repomsgdct[reponame][shalst[i].rstrip()] = msglst[i].rstrip()
        repodiffdct[reponame][shalst[i].rstrip()] = difflst[i].rstrip()

    msgf.close()
    repof.close()
    shaf.close()

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

def findMultipleNote(diff):
    lines = diff.split(" <nl> ")
    addLines = []
    delLines = []
    for i in lines:
        if "+ *" in i or "+ / * *" in i:
            addLines.append(i[2::])
        elif "- *" in i or "- / * *" in i:
            delLines.append(i[2::])

    addret = []
    delret = []
    if len(addLines) != 0:
        addret = ("Add multiple note: " + " ".join(addLines)).split()
    if len(delLines) != 0:
        delret = ("Del multiple note: " + " ".join(delLines)).split()
    return addret,delret

def checkIfNoOutput(CSout):
    Mindex = CSout.find("Modifications")
    if Mindex == -1:
        if len(CSout.split()) >= 10:
            return True
        else:
            return False
    tmplst = CSout[Mindex::].split("Modifications")
    for i in tmplst:
        if len(i.split()) >= 5:
            return True
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




def processFile(root,filename):
    path = os.path.join(root, filename)
    alterdic = readAlterFile(os.path.join(alterFoldPath,filename))
    global source_CS_freq_count
    global source_Diff_freq_count
    global target_freq_count
    global nonoutputcnt

    f = open(path,"r",encoding = "UTF-8")
    print(path)
    flst = f.readlines()

    f.close()
    random.shuffle(flst)
    cnt = 0
    filteredcnt = 0

    nonoutputfile = open("nonoutput.csv","a",encoding = "UTF-8")

    for i in range(len(flst)):
        if nonJavaFileStr in flst[i]:
            continue
        CSlst = flst[i].rstrip().split()
        if len(CSlst) <= 2:
            print(CSlst)
            continue
        if CSlst[1] in alterdic:
            CSlst = alterdic[CSlst[1]].rstrip().split()
            print(CSlst[1])
        if CSlst[2] == "处理异常" or CSlst[2] == "无明显变化" or CSlst[2] == "输出超长":
            continue
        if len(CSlst) >= CSmaxlen:
            continue

        if not checkIfNoOutput(" ".join(CSlst[2::])):
            nonoutputcnt += 1
            nonoutputfile.write(CSlst[0]+","+CSlst[1]+",")
            nonoutputfile.write(" ".join(CSlst[2::]))
            nonoutputfile.write(",")
            nonoutputfile.write(repodiffdct.get(CSlst[0],dict()).get(CSlst[1],""))
            nonoutputfile.write("\n")
            #continue

        msg = repomsgdct.get(CSlst[0],dict()).get(CSlst[1],"")
        msg = msgLemmatization(msg)
        if not checkmsg(msg):
            continue

        diff = repodiffdct.get(CSlst[0],dict()).get(CSlst[1],"")
        #if fileFilter(diff):#过滤非java文件
        #    filteredcnt += 1
        #    continue

        add_token,del_token = getAddAndDelToken(diff)
        add_mul_note,del_mul_note = findMultipleNote(diff)
        #print(add_mul_note,del_mul_note)
        tmplstCS = CSlst[2::] + add_mul_note + del_mul_note
        CScode_token = fixCodeToken(replaceTypeDescribe(tmplstCS))

        tmpDiffdic = dict()
        tmpDiffdic["add_tokens"] = add_token
        tmpDiffdic["del_tokens"] = del_token
        tmpDiffdic["commit_tokens"] = msg
        tmpDiffdic["repo"] = CSlst[0]
        tmpDiffdic["sha"] = CSlst[1]

        tmpCSdic = dict()
        tmpCSdic["code_tokens"] = CScode_token
        tmpCSdic["docstring_tokens"] = msg
        tmpCSdic["repo"] = CSlst[0]
        tmpCSdic["sha"] = CSlst[1]

        tmpCBDiffdic = dict()
        tmpCBDiffdic["code_tokens"] = fixCodeToken(diff)
        tmpCBDiffdic["docstring_tokens"] = msg
        tmpCBDiffdic["repo"] = CSlst[0]
        tmpCBDiffdic["sha"] = CSlst[1]

        pairDiffStr = (diff," ".join(msg))
        pairCSStr = (" ".join(CScode_token)," ".join(msg))

        num = cnt % pctsum

        if num < trainpct + validpct:
            #if len(pairDiffStr[0].split()) < CSmaxlen: 
            for wod in diff.split():
                source_Diff_vocabdic[wod] = source_Diff_vocabdic.get(wod, 0) + 1
                source_Diff_freq_count += 1
            for wod in CScode_token:
                source_CS_vocabdic[wod] = source_CS_vocabdic.get(wod, 0) + 1
                source_CS_freq_count += 1
            for wod in msg:
                target_vocabdic[wod] = target_vocabdic.get(wod, 0) + 1
                target_freq_count += 1

        if num < trainpct:
            tmpCSdic["partition"] = "train"
            tmpCBDiffdic["partition"] = "train"
            trainCSlst.append(tmpCSdic)
            trainCodeBertDifflst.append(tmpCBDiffdic)
            trainDifflst.append(tmpDiffdic)
            sourceCSPairLst.append(pairCSStr)
            if len(pairDiffStr[0].split()) < Ptrmaxlen:
                sourceDiffPairLst.append(pairDiffStr)
        elif num < trainpct + validpct:
            tmpCSdic["partition"] = "valid"
            tmpCBDiffdic["partition"] = "valid"
            validCSlst.append(tmpCSdic)
            validCodeBertDifflst.append(tmpCBDiffdic)
            validDifflst.append(tmpDiffdic)
            validCSPairLst.append(pairCSStr)
            if len(pairDiffStr[0].split()) < Ptrmaxlen:
                validDiffPairLst.append(pairDiffStr)
        else:
            tmpCSdic["partition"] = "test"            
            tmpCBDiffdic["partition"] = "test"
            testCSlst.append(tmpCSdic)
            testCodeBertDifflst.append(tmpCBDiffdic)
            testDifflst.append(tmpDiffdic)
            testCSPairLst.append(pairCSStr)
            if len(pairDiffStr[0].split()) < Ptrmaxlen:    
                testDiffPairLst.append(pairDiffStr)

        cnt += 1
    
    nonoutputfile.close()
    print(filteredcnt)

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
    getdct("train")
    getdct("valid")
    getdct("test")

    nonoutputfile = open("nonoutput.csv","w",encoding = "UTF-8")
    nonoutputfile.close()

    for root, dirs, files in os.walk(foldpath):
        for f in files:
            processFile(root,f)

    getvocabfile(case_name_diff,source_Diff_vocabdic,source_Diff_freq_count,".vocab.source")
    getvocabfile(case_name_diff,target_vocabdic,target_freq_count,".vocab.target")
    getSourceFileAndTargetFile(case_name_diff,validDiffPairLst,".eval")
    getSourceFileAndTargetFile(case_name_diff,sourceDiffPairLst,".train")
    getSourceFileAndTargetFile(case_name_diff,testDiffPairLst,".test")

    getvocabfile(case_name_CS,source_CS_vocabdic,source_CS_freq_count,".vocab.source")
    getvocabfile(case_name_CS,target_vocabdic,target_freq_count,".vocab.target")
    getSourceFileAndTargetFile(case_name_CS,validCSPairLst,".eval")
    getSourceFileAndTargetFile(case_name_CS,sourceCSPairLst,".train")
    getSourceFileAndTargetFile(case_name_CS,testCSPairLst,".test")

    if not os.path.exists(case_name_mcmdCommitBertDiff):
       os.mkdir(case_name_mcmdCommitBertDiff)
    writefile(trainDifflst,case_name_mcmdCommitBertDiff + "train.jsonl")
    writefile(validDifflst,case_name_mcmdCommitBertDiff + "valid.jsonl")
    writefile(testDifflst,case_name_mcmdCommitBertDiff + "test.jsonl")

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

    print(nonoutputcnt)

main()

    