from nltk.translate.bleu_score import sentence_bleu
from nltk.translate.bleu_score import SmoothingFunction
import json

CSbeforegoldname = r"newoutputResult\CSFix60.gold.post"
CSbeforename = r"newoutputResult\CSFix60.output.post"
CSbeforetestfile = r"mcmdCBCSPTRFFirafix60\test.jsonl"

CSaftergoldname = r"newoutputResult\CSN1115.gold.post"
CSaftername = r"newoutputResult\CSN1115.output.post"
CSaftertestfile = r"mcmdCBCSPTRFFiraN9\test.jsonl"

# CSaftergoldname = r"NNGCase\test.gold"
# CSaftername = r"NNGCase\test.msg"
# CSaftertestfile = r"mcmdDIFFPTRNEWFFirafix18\test.jsonl"

# CSaftergoldname = r"newoutputResult\DiffFiraFull.gold.post"
# CSaftername = r"newoutputResult\DiffFiraFull.output.post"
# CSaftertestfile = r"mcmdDIFFPTRNEWFFiradefault\test.jsonl"

# CSaftergoldname = r"newoutputResult\CSFix24.gold.post"
# CSaftername = r"newoutputResult\CSFix24.output.post"
# CSaftertestfile = r"mcmdCBCSPTRFFirafix24\test.jsonl"

diffgoldname = r"newoutputResult\DiffFiraFull.gold.post"
diffname = r"newoutputResult\DiffFiraFull.output.post"
difftestfile = r"mcmdDIFFPTRNEWFFiradefault\test.jsonl"

Firagoldname = r"FIRA-ICSE-main\OUTPUT\ground_truth"
Firaname = r"FIRA-ICSE-main\OUTPUT\output_fira"
all_index = json.load(open(r"FIRA-ICSE-main\all_index","r"))
linenumtestlst = all_index["test"]



# outputname = r"analyse.csv"
difftopoutput = r"PtrBeforeresultTopN11_Fira.csv"
CStopoutput = r"PtrAfterresultTopN11_Fira.csv"
repooutput = r"reporesultfixN11_Fira.csv"
# difforioutput = r"DiffTop500.csv"
# CSorioutput = r"CSTop500.csv"

linenumToDiff = dict()
linenumToFira = dict()
linenumToCS2 = dict()
CStestlst = []
difftestlst = []

fCSgold = open(CSbeforegoldname,"r",encoding="utf-8").read().split("\n")
fCSgen = open(CSbeforename,"r",encoding="utf-8").read().split("\n")

fAftergold = open(CSaftergoldname,"r",encoding="utf-8").read().split("\n")
fAfterCSgen = open(CSaftername,"r",encoding="utf-8").read().split("\n")

fdiffgold = open(diffgoldname,"r",encoding="utf-8").read().split("\n")
fdiffgen = open(diffname,"r",encoding="utf-8").read().split("\n")

fFiragold = open(Firagoldname,"r",encoding="utf-8").read().split("\n")
fFiragen = open(Firaname,"r",encoding="utf-8").read().split("\n")

res = []

CScnt = 0
CSAftercnt = 0
diffcnt = 0
Firacnt = 0

CSrepodict = dict()
CSAfterrepodict = dict()
Diffrepodict = dict()
Firarepodict = dict()

CSrepocnt = dict()
CSAfterrepocnt = dict()
Diffrepocnt = dict()
Firarepocnt = dict()

with open(difftestfile,"r",encoding="utf-8") as f:
    lst = f.read().split("\n")
    for i in range(len(lst)):
        if lst[i] == "":
            continue
        casedict = json.loads(lst[i])
        linenumToDiff[casedict["fira_line"]] = ((" ".join(casedict['code_tokens'])).replace(',','$'),sentence_bleu([fdiffgold[i].split()],fdiffgen[i].split(),smoothing_function=SmoothingFunction().method1),fdiffgen[i])

with open(CSaftertestfile,"r",encoding="utf-8") as f:
    lst = f.read().split("\n")
    for i in range(len(lst)):
        if lst[i] == "":
            continue
        casedict = json.loads(lst[i])
        linenumToCS2[casedict["fira_line"]] = ((" ".join(casedict['code_tokens'])).replace(',','$'),sentence_bleu([fAftergold[i].split()],fAfterCSgen[i].split(),smoothing_function=SmoothingFunction().method1),fAfterCSgen[i])


for i in range(len(linenumtestlst)):

    linenumToFira[linenumtestlst[i]] = (sentence_bleu([fFiragold[i].split()],fFiragen[i].split(),smoothing_function=SmoothingFunction().method1),fFiragen[i])

with open(CSbeforetestfile,"r",encoding="utf-8") as f:
    lst = f.read().split("\n")

    print(len(lst),len(fCSgold),len(fCSgen),len(fAfterCSgen))

    for i in range(len(lst)):
        if lst[i] == "":
            continue
        casedict = json.loads(lst[i])
        CSbleu = sentence_bleu([fCSgold[i].split()],fCSgen[i].split(),smoothing_function=SmoothingFunction().method1)
        
        linenum = casedict["fira_line"]
        reponame = casedict["repo"]


        if linenum not in linenumToDiff:
            print("Diff not found:",linenum)
            continue

        if linenum not in linenumToFira:
            print("Fira not found:",linenum)
            continue

        if linenum not in linenumToCS2:
            print("CS2 not found:",linenum)
            continue

        CSAfterbleu = linenumToCS2[linenum][1]
        diffbleu = linenumToDiff[linenum][1]
        Firableu = linenumToFira[linenum][0]


        CSstr = (" ".join(json.loads(lst[i].strip())['code_tokens'])).replace(',','$')
        CS2str = linenumToCS2[linenum][0]
        Diffstr = linenumToDiff[linenum][0]

        gold = fCSgold[i]
        CSgen = fCSgen[i]
        CSAftergen = linenumToCS2[linenum][2]
        Diffgen = linenumToDiff[linenum][2]
        Firagen = linenumToFira[linenum][1]

        CScnt += CSbleu
        CSAftercnt += CSAfterbleu
        diffcnt += diffbleu
        Firacnt += Firableu

        CSrepodict[reponame] = CSrepodict.get(reponame,0) + CSbleu
        CSAfterrepodict[reponame] = CSAfterrepodict.get(reponame,0) + CSAfterbleu
        Diffrepodict[reponame] = Diffrepodict.get(reponame,0) + diffbleu
        Firarepodict[reponame] = Firarepodict.get(reponame,0) + Firableu

        CSrepocnt[reponame] = CSrepocnt.get(reponame,0) + 1
        CSAfterrepocnt[reponame] = CSAfterrepocnt.get(reponame,0) + 1
        Diffrepocnt[reponame] = Diffrepocnt.get(reponame,0) + 1
        Firarepocnt[reponame] = Firarepocnt.get(reponame,0) + 1

        restuples = (CSAfterbleu - Firableu, CSbleu,CSAfterbleu, diffbleu,Firableu,gold,CSgen,CSAftergen,Diffgen,Firagen,CSstr,CS2str,Diffstr,linenum)
        #restuples = (CSAfterbleu - Firableu, CSbleu,CSAfterbleu, diffbleu,Firableu,gold,CSgen,CSAftergen,Diffgen,Firagen,CSstr,CS2str,Diffstr,linenum)

        res.append(restuples)

res.sort()


# with open(outputname,"w",encoding="utf-8") as cf:
#     cf.write("No.,bleudiff,CSbleu,diffbleu,gold,CSout,diffout\n")
#     #cf.write("---,---,---,---,---,---,---\n")
#     for i in range(len(res)):
#         cf.write(str(res[i][6])+","+str(res[i][0])+","+str(res[i][1])+","+str(res[i][3])+","+res[i][5]+","+res[i][2]+","+res[i][4]+"\n")

with open(difftopoutput,"w",encoding="utf-8") as cf:
    cf.write("LineNo.,bleuDiff,CSbleu,CS2bleu,Diffbleu,Firableu,gold,CSgen,CS2gen,Diffgen,Firagen,CSout,CS2out,diffout\n")
    #cf.write("---,---,---,---,---,---,---,---,---\n")
    for i in range(2000):
        cf.write(str(res[i][13])+","+str(res[i][0])+","+str(res[i][1])+","+str(res[i][2])+","+str(res[i][3])+","+str(res[i][4])+","+res[i][5]+","+res[i][6]+","+res[i][7]+","+res[i][8]+","+res[i][9]+","+res[i][10]+","+res[i][11]+","+res[i][12]+"\n")

'''
with open(difforioutput,"w",encoding="utf-8") as cf:
    cf.write("No.,CSbleu,diffbleu,CSout,diffout\n")
    cf.write("---,---,---,---,---\n")
    for i in range(500):
        cf.write(str(res[i][6])+","+str(res[i][1])+","+str(res[i][3])+","+CStestlst[res[i][6]]+","+difftestlst[res[i][6]]+"\n")
'''

with open(CStopoutput,"w",encoding="utf-8") as cf:
    cf.write("LineNo.,bleuDiff,CSbleu,CS2bleu,Diffbleu,Firableu,gold,CSgen,CS2gen,Diffgen,Firagen,CSout,CS2out,diffout\n")
    #cf.write("No.,bleudiff,CSbleu,diffbleu,gold,CSout,diffout,CSout,diffout\n")
    #cf.write("---,---,---,---,---,---,---,---,---\n")
    for i in range(len(res)-1,len(res)-1001,-1):
        cf.write(str(res[i][13])+","+str(res[i][0])+","+str(res[i][1])+","+str(res[i][2])+","+str(res[i][3])+","+str(res[i][4])+","+res[i][5]+","+res[i][6]+","+res[i][7]+","+res[i][8]+","+res[i][9]+","+res[i][10]+","+res[i][11]+","+res[i][12]+"\n")
        # cf.write(str(res[i][6])+","+str(res[i][0])+","+str(res[i][1])+","+str(res[i][3])+","+res[i][5]+","+res[i][2]+","+res[i][4]+","+CStestlst[res[i][6]]+","+difftestlst[res[i][6]]+"\n")

'''
with open(CSorioutput,"w",encoding="utf-8") as cf:
    cf.write("No.,CSbleu,diffbleu,CSout,diffout\n")
    cf.write("---,---,---,---,---\n")
    for i in range(length-1,length-501,-1):
        cf.write(str(res[i][6])+","+str(res[i][1])+","+str(res[i][3])+","+CStestlst[res[i][6]]+","+difftestlst[res[i][6]]+"\n")
'''

repolist = []

for name, v in CSrepodict.items():
    repolist.append([name,str(CSrepodict[name]),str(CSAfterrepodict[name]),str(Diffrepodict[name]),str(Firarepodict[name])])

with open(repooutput,"w",encoding="utf-8") as cf:
    cf.write("RepoName,CS,CS2,Diff,Fira\n")
    for i in range(len(repolist)):
        cf.write(",".join(repolist[i]) + "\n")

print(CScnt / len(res),CSAftercnt / len(res), diffcnt / len(res), Firacnt / len(res))

# fgold.close()
# fCS.close()
# fdiff.close()