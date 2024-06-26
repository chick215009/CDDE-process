import os
import json

foldpath = "./output7"
noneJavaWords = "Here are some none java files diff"

MethodNameDict = dict()
ClassNameDict = dict()


def processFile(root,filename):
    fileN = filename[:-4:]
    txtpath = os.path.join(root, filename)
    jsonpath = os.path.join(root,fileN + ".json")
    txtf = open(txtpath,"r",encoding = "UTF-8")
    jsonf = open(jsonpath,"r",encoding = "UTF-8")
    print(txtpath)
    print(jsonpath)
    txtflst = txtf.readlines()
    jsonflst = jsonf.readlines()
    txtf.close()
    jsonf.close()

    MethodNameDict[fileN] = dict()
    ClassNameDict[fileN] = dict()

    for i in range(len(txtflst)):
        if noneJavaWords in txtflst[i]:
            continue

        CSlst = txtflst[i].rstrip().split()
        MethodNameDict[fileN][CSlst[1]] = json.loads(jsonflst[2*i])
        ClassNameDict[fileN][CSlst[1]] = json.loads(jsonflst[2*i + 1])


    





for root, dirs, files in os.walk(foldpath):
    for f in files:
        if f.endswith(".txt"):
            processFile(root,f)


with open("MethodName.json","w") as fp:
    json.dump(MethodNameDict,fp)
    fp.write("\n")

with open("ClassName.json","w") as fp:
    json.dump(ClassNameDict,fp)
    fp.write("\n")