#!/usr/local/bin/python

# Malware Database (malc0de) :: malc0de Balcklist Parser

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
    alignment="%-*s%-*s%-*s%-*s%*s"
    column1_width=20
    column2_width=20
    column3_width=20
    column4_width=20
    column5_width=20
    MalOutput.write(alignment % (column1_width, "MalType", column2_width, "MalIPaddress", column3_width, "Port", column4_width, "Source", column5_width, "Date\n"))
    for mal_name, mal_ipaddr in blocklist.items():
        for each_ip in mal_ipaddr.split(" ")[1:]:
            MalOutput.write( alignment % (column1_width, mal_name, column2_width, each_ip, column3_width, port, column4_width, source, column5_width, today+"\n"))
    MalOutput.close()



#sourceFetch()
sourceParse()
createOutput()












