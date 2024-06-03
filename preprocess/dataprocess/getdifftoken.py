import difflib
import os
import re

foldname = r"./download-89411"

difftoken = []
diffmark = []
msg = []

def splt(matched):
    return " " + matched.group() + " "

def compare_files(f1,f2,msg):

    difftokenlst = []
    diffmarklst = []
    msglst = []

    with open(f1,"r",encoding="utf-8") as beforefile, open(f2,"r",encoding="utf-8") as afterfile:
        lst = list(difflib.unified_diff(beforefile.readlines(),afterfile.readlines()))

        for i in lst[2::]:
            str = re.sub(r"\W",splt,i)
            str = str.replace("\n"," <nl>")
            linelst = str.split()
            if linelst[0] == '@' and linelst[1] == '@':
                difftokenlst.append("<nb>")
                diffmarklst.append(2)
            elif linelst[0] == '-':
                for p in linelst[1::]:
                    difftokenlst.append(p)
                    diffmarklst.append(1)
            elif linelst[0] == '?':
                pass
            elif linelst[0] == '+':
                for p in linelst[1::]:
                    difftokenlst.append(p)
                    diffmarklst.append(3)
            else:
                for p in linelst:
                    difftokenlst.append(p)
                    diffmarklst.append(2)
    
    with open(msg,"r",encoding="utf-8") as fp:
        msglst = fp.read().split()


    return difftokenlst,diffmarklst,msglst


for root, dirs, files in os.walk(foldname):
    for f in dirs:
        nowfoldname = os.path.join(root,f)
        lst = os.path.join(root,f).split("\\")
        if len(lst) == 4:
            f1name = ""
            f2name = ""
            for r1,d1,f1 in os.walk(nowfoldname):
                for p in f1:
                    if "A@" in p:
                        f1name = os.path.join(nowfoldname,p)
                    
                    if "B@" in p:
                        f2name = os.path.join(nowfoldname,p)

            a,b,c = compare_files(f1name,f2name,nowfoldname + "/realMsg.txt")
            difftoken.append(a)
            diffmark.append(b)
            msg.append(c)