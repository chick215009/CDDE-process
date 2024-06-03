import json

suffixbefore = ""
suffixafter = "10"
suffixoutput = "11"

methodNamef = open(r"F:\codisumCSoutput\MethodName" + suffixbefore + ".json","r")
methodNamedct = json.load(methodNamef)

classNamef = open(r"F:\codisumCSoutput\ClassName" + suffixbefore + ".json","r")
classNamedct = json.load(classNamef)

# fieldNamef = open(r"F:\codisumCSoutput\FieldName" + suffixbefore + ".json","r")
# fieldNamedct = json.load(fieldNamef)

methodNameAf = open(r"F:\codisumCSoutput\MethodName" + suffixafter + ".json","r")
methodNameAdct = json.load(methodNameAf)

classNameAf = open(r"F:\codisumCSoutput\ClassName" + suffixafter + ".json","r")
classNameAdct = json.load(classNameAf)

# fieldNameAf = open(r"F:\codisumCSoutput\FieldName" + suffixafter + ".json","r")
# fieldNameAdct = json.load(fieldNameAf)


for key,value in methodNamedct.items():
    if key not in methodNameAdct:
        methodNameAdct[key] = value

for key,value in classNamedct.items():
    if key not in classNameAdct:
        classNameAdct[key] = value

# for key,value in fieldNamedct.items():
#     if key not in fieldNameAdct:
#         fieldNameAdct[key] = value

json.dump(methodNameAdct,open(r"F:\codisumCSoutput\MethodName" + suffixoutput + ".json","w"))
json.dump(classNameAdct,open(r"F:\codisumCSoutput\ClassName" + suffixoutput + ".json","w"))
# json.dump(fieldNameAdct,open(r"F:\codisumCSoutput\FieldName" + suffixoutput + ".json","w"))