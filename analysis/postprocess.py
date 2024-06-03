casename = r"newoutputResult\Kimi"

goldname = casename + ".gold"
outputname = casename + ".output"

def removeid(x):
    return " ".join(x.split()[1::])

with open(goldname,"r",encoding="utf-8") as f:
    fgold = f.readlines()
    fgold = map(removeid,fgold)

    with open(goldname + ".post","w",encoding="utf-8") as cf:
        cf.write("\n".join(fgold))

with open(outputname,"r",encoding="utf-8") as f:
    foutput = f.readlines()
    foutput = map(removeid,foutput)

    with open(outputname + ".post","w",encoding="utf-8") as cf:
        cf.write("\n".join(foutput))