#!/usr/local/bin/python

# abuse.ch SpyEye IP blocklist 

#from structshape import structshape
from datetime import date
import os

nfquery = "/usr/local/nfquery/"
sourcepath = nfquery + "sources/SpyEyeTracker/"
outputpath = nfquery + "outputs/SpyEyeTracker/"
mal_name="SpyEyeTracker"
blocklist={}

def sourceFetch():
    SpyEyeTracker_bl_source = "https://spyeyetracker.abuse.ch/blocklist.php?download=ipblocklist  "
    os.system("fetch  " + SpyEyeTracker_bl_source)
    os.system("mv blocklist.php* " + sourcepath + "blocklist")


def sourceParse():    
    blfile=open(sourcepath + "blocklist","r")
    blocklist[mal_name]=""
    for i in blfile.readlines()[6:]:
        mal_ipaddr = i.split("\n")[0]
        blocklist[mal_name]=blocklist[mal_name] + " " + mal_ipaddr 

def createOutput():
    today=date.today().isoformat()
    source="SpyEyeTracker"
    port="-"
    MalOutput=open(outputpath + "MalOutput.SpyEyeTracker","w")
    headline="MalType\t\t\tMalIPaddress\t\t\tPort\t\t\tSource\t\t\tDate\n"
    MalOutput.write(headline)
    for mal_name, mal_ipaddr in blocklist.items():
        for each_ip in mal_ipaddr.split(" ")[1:]:
            tabs="\t\t\t"
            line=mal_name + tabs + each_ip + tabs + port + tabs + source + tabs + today + "\n"
            MalOutput.write(line)
    MalOutput.close()



#sourceFetch()
sourceParse()
createOutput()
#print structshape(blocklist) 
#for key, value in blocklist.items():
#    print str(key) + "   " + str(value) + "\n"












