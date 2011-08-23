#!/usr/local/bin/python

# Malware Database (AMaDa) :: AMaDa Blocklist Parser



#from structshape import structshape
from datetime import date
import os

nfquery = "/usr/local/nfquery/"
sourcepath = nfquery + "sources/amada/"
outputpath = nfquery + "outputs/amada/"
blocklist={}

def sourceFetch():
    amada_bl_source = "http://amada.abuse.ch/blocklist.php?download=ipblocklist  "
    os.system("fetch  " + amada_bl_source)
    os.system("mv block* " + sourcepath + "blocklist")


def sourceParse():    
    blfile=open(sourcepath + "blocklist","r")
    for i in blfile.readlines()[5:]:
        print i
        mal_ipaddr=i.split(" ")[0]
        mal_name=i.split(" ")[2].split("\n")[0]
        if (mal_name in blocklist.keys()):
            blocklist[mal_name] = blocklist[mal_name] + " " + mal_ipaddr
        else:
            blocklist[mal_name] = mal_ipaddr

def createOutput():
    today=date.today().isoformat()
    source="AMaDa"
    port="-"
    MalOutput=open(outputpath + "MalOutput","w")
    headline="MalType\t\t\tMalIPaddress\t\t\tPort\t\t\tSource\t\t\tDate\n"
    MalOutput.write(headline)
    for mal_name, mal_ipaddr in blocklist.items():
        for each_ip in mal_ipaddr.split(" "):
            tabs="\t\t\t"
            line=mal_name + tabs + each_ip + tabs + port + tabs + source + tabs + today + "\n"
            MalOutput.write(line)
    MalOutput.close()



#sourceFetch()
sourceParse()
createOutput()
#print structshape(blocklist) 
for key, value in blocklist.items():
    print str(key) + "   " + str(value) + "\n"












