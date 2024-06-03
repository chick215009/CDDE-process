from openai import OpenAI
import json
import time
import timeout_decorator
import threading

import os
# os.environ["http_proxy"] = "http://localhost:7890"
# os.environ["https_proxy"] = "http://localhost:7890"

testFileName = r"E:\soter2Ai\mcmdDIFFPTRNEWFFirafix18\test.jsonl"

client = OpenAI(
    api_key="your key",
)

prefix = "Here is a code diff: \n"
suffix = "Please identify the Camel-Case words in code diff and output them according to Method Name, Class Name, FieldName, TypeName and Identifier.\n Please extract comments and annotation information that changed from code diff and output them.\n"

indexdic = json.load(open(r"E:\soter2Ai\FIRA-ICSE-main\all_index","r"))
testlinelst = indexdic["test"]

#testlst = open(r"E:\soter2Ai\mcmdCBCSPTRFFirafix60\test.jsonl","r").read().split("\n")
testlst = open(testFileName,"r").read().split("\n")

# testlinelst = json.load(open("outputnotfoundlst.json","r"))
difff = open(r"E:\soter2Ai\codisumdiff.json","r")
repodiffdct = json.load(difff)
line2hash = json.load(open(r"D:\BaiduNetdiskDownload\data\data\line2hash1.json","r"))

# ff = testlinelst.index(28834)
# bb = testlinelst.index(33800)

#difftext = r"diff --git a/OsmAnd/src/net/osmand/plus/views/PointLocationLayer.java b/OsmAnd/src/net/osmand/plus/views/PointLocationLayer.java\nindex 5373fd0cc9..eb0786a0ee 100644\n--- a/OsmAnd/src/net/osmand/plus/views/PointLocationLayer.java\n+++ b/OsmAnd/src/net/osmand/plus/views/PointLocationLayer.java\n@@ -70,7 +70,7 @@ public class PointLocationLayer extends OsmandMapLayer {\n \n \t\n \tprivate RectF getHeadingRect(int locationX, int locationY){\n-\t\tint rad = (int) (view.getDensity() * 55);\n+\t\tint rad = (int) (view.getDensity() * 60);\n \t\treturn new RectF(locationX - rad, locationY - rad, locationX + rad, locationY + rad);\n \t}\n \t\n"

outfile = open("KimiEnhance","w")

def getsummary(difftext):
    res = client.chat.completions.create(
        model="moonshot-v1-8k",
        messages=[{"role": "user", "content": prefix + difftext + suffix}],
    )

    return res.choices[0].message.content


def get_completion_by_loop(get_completion,prompt):
    while True:
        try:
            response = get_completion(prompt)
            # Check if the response has a value
            if response is not None:
                break  # If the response has a value, jump out of the loop
        except timeout_decorator.TimeoutError as e:
            print(f"Timeout exception: {e}, Retrying currently...")
        except Exception as e:
            sec = 30
            print(f"An exception has occurred: {e}, Retrying in {sec} seconds...")
            time.sleep(sec)  # Wait and rerun the code

    return response

# for i in range(len(testlst[:10:])):
#     dic = json.loads(testlst[i])

#     difftext = " ".join(dic["code_tokens"])

#     # for j in range(12):
#     #     difftext = difftext.replace("Ty" + str(j) + " ","")

#     # outfile.write(reponame + " " + hashcode + " ")

#     outfile.write(str(i) + " " + get_completion_by_loop(getsummary,difftext).replace("\n"," "))

#     outfile.write("\n")

#     if i % 100 == 0:
#         print(i)


class MyThread(threading.Thread):
    def __init__(self,startpos,endpos,n,difflst):
        super().__init__()
        self.startpos = startpos
        self.endpos = endpos
        self.n = n
        self.difflst = difflst

    def run(self) -> None:
        print("Thread",self.n,":",self.startpos,self.endpos)
        outfile = open("KimiEnhance" + str(self.n) + ".json","w",encoding="utf-8")

        for i in range(self.startpos,self.endpos):    
            dic = json.loads(self.difflst[i])

            difftext = " ".join(dic["code_tokens"])

            # for j in range(12):
            #     difftext = difftext.replace("Ty" + str(j) + " ","")

            # outfile.write(reponame + " " + hashcode + " ")

            outfile.write(str(i) + " " + get_completion_by_loop(getsummary,difftext).replace("\n"," "))

            outfile.write("\n")

            # outfile.write("<STPWPW> \"" + str(i) + "\": \"")

            # outfile.write(get_completion_by_loop(getsummary,difftext))

            # #print()
            # outfile.write("\" <ENDWPW>\n")

            if i % 100 == 0:
                print(self.n,i)

t1 = MyThread(0,1000,1,testlst)
t1.start()
t2 = MyThread(1000,2000,2,testlst)
t2.start()
t3 = MyThread(2000,3000,3,testlst)
t3.start()
t4 = MyThread(3000,4000,4,testlst)
t4.start()
t5 = MyThread(4000,5000,5,testlst)
t5.start()
t6 = MyThread(5000,6000,6,testlst)
t6.start()
t7 = MyThread(6000,7000,7,testlst)
t7.start()
t8 = MyThread(7000,len(testlst),8,testlst)
t8.start()