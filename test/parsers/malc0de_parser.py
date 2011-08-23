#!/usr/local/bin/python

# Malware Database (AMaDa) :: AMaDa Blocklist Parser



#from structshape import structshape
from datetime import date
import os

nfquery = "/usr/local/nfquery/"
sourcepath = nfquery + "sources/malc0de/"
outputpath = nfquery + "outputs/malc0de/"
mal_name="DNSBlackhole"
blocklist={}

def sourceFetch():
    malc0de_bl_source = "http://malc0de.com/bl/IP_Blacklist.txt  "
    os.system("fetch  " + malc0de_bl_source)
    os.system("mv IP_Blacklist.txt " + sourcepath)


def sourceParse():    
    blfile=open(sourcepath + "IP_Blacklist.txt","r")
    blocklist[mal_name]=""
    for i in blfile.readlines()[4:]:
        mal_ipaddr = i.split("\n")[0]
        blocklist[mal_name]=blocklist[mal_name] + " " + mal_ipaddr 

def createOutput():
    today=date.today().isoformat()
    source="malc0de DNS Blackhole"
    port="-"
    MalOutput=open(outputpath + "MalOutput.malc0de","w")
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












