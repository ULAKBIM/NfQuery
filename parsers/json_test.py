#!/usr/local/bin/python

# Malware Database (AMaDa) :: AMaDa Blocklist Parser

from datetime import date
import os
import json 

nfquery = "/usr/local/nfquery/"
sourcepath = nfquery + "sources/amada/"
outputpath = nfquery + "outputs/amada/"
blocklist={}

class Query:
    queryid=1
    ip=""
    domain=""
    port=1
    sourcename=""
    threattype=""
    creationtime="01.01.1111"



def sourceFetch():
    amada_bl_source = "http://amada.abuse.ch/blocklist.php?download=ipblocklist  "
    os.system("fetch  " + amada_bl_source)
    os.system("mv block* " + sourcepath + "blocklist")


def sourceParse():    
    blfile=open(sourcepath + "blocklist","r")
    for i in blfile.readlines()[5:]:
        mal_ipaddr=i.split(" ")[0]
        mal_name=i.split(" ")[2].split("\n")[0]
        if (mal_name in blocklist.keys()):
            blocklist[mal_name] = blocklist[mal_name] + " " + mal_ipaddr
        else:
            blocklist[mal_name] = mal_ipaddr


#def createQuery():
def testJASON():
    # 1) Define a JSON schema for the query data structure
    with open('test.jason', mode='w', encoding='utf-8') as queryfile:
        json.dump(blocklist, jasonfile, indent=1)
    # 2) Load the structure values with fetched values from the database and fill the blank values as FALSE mean don't give up any field with a blank or null character, it should be FALSE
    #or some usable data.
    
    # 3) Insert these structures to a database, so prepare a database structure for the structures that will be stored in there. 
    queryid=1
    today=date.today().isoformat()
    source="AMaDa"
    port="-"
    MalOutput=open(outputpath + "MalOutput.amada","w")
    alignment="%-*s%-*s%-*s%-*s%*s"

    ########################################################################################
    # 1) Define a JSON schema for the query data structure
    ########################################################################################
    # query id       : Index of the query 
    # ip             : Aggregated ip list of the selected blocklist source
    # domain         : Aggregated domainlist of the selected blocklist source
    # port           : Port Information 
    # source name    : Selected security source name for exm : amada.ch or spyeyetracker
    # threat type    : Type of the threat such as Botnet, SPAM, DNS Blocklist etc.
    # creation time  : Creation time of this query that will be used when checking
    #                  if there is an update for the created query
    #
    ########################################################################################



    MalOutput.write(alignment % (column1_width, "MalType", column2_width, "MalIPaddress", column3_width, "Port", column4_width, "Source", column5_width, "Date\n"))
    for mal_name, mal_ipaddr in blocklist.items():
        for each_ip in mal_ipaddr.split(" "):
            MalOutput.write( alignment % (column1_width, mal_name, column2_width, each_ip, column3_width, port, column4_width, source, column5_width, today+"\n"))
    MalOutput.close()

    
    

#sourceFetch()
#sourceParse()
#createOutput()

q=Query()
print q.queryid
