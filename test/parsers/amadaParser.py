#!/usr/local/bin/python

# Malware Database (AMaDa) :: AMaDa Blocklist Parser

from datetime import date
from query import Query
import os
import sys 

#from querygenerator import generateQuery

nfquery = "/usr/local/nfquery/"
sourcepath = nfquery + "sources/amada/"
outputpath = nfquery + "outputs/amada/"
blocklist={}

#print __file__
#sys.exit()


def fetchSource(source):
    os.system("fetch -o " + sourcepath + source + " " + __file__ "file")


def parseSource():    
    blfile=open(sourcepath + "blocklist","r")
    for i in blfile.readlines()[5:]:
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
    MalOutput=open(outputpath + "MalOutput.amada","w")
    alignment="%-*s%-*s%-*s%-*s%*s"
    column1_width=20
    column2_width=20
    column3_width=15
    column4_width=15
    column5_width=15
    MalOutput.write(alignment % (column1_width, "MalType", column2_width, "MalIPaddress", column3_width, "Port", column4_width, "Source", column5_width, "Date\n"))
    for mal_name, mal_ipaddr in blocklist.items():
        for each_ip in mal_ipaddr.split(" "):
            print alignment % (column1_width, mal_name, column2_width, each_ip, column3_width, port, column4_width, source, column5_width, today) 
            MalOutput.write( alignment % (column1_width, mal_name, column2_width, each_ip, column3_width, port, column4_width, source, column5_width, today+"\n"))
    MalOutput.close()



    def __init__(self, source_name, threat_type, threat_desc, creation_time, 
                             ip=None, domain=None, port=None):

def createQuery(sourcefile):
    source_file=open(sourcefile,"r")
    ''' 
        Parse file line by line and extract ip information
    '''
    # Prepare a query object for storing extracted information into 
    for line in sourcefile.readlines()[5:]:
        mal_ipaddr=line.split(" ")[0]
        mal_name=line.split(" ")[2].split("\n")[0]
        
    
    today=date.today().isoformat()



fetchSource("http://amada.abuse.ch/blocklist.php?download=ipblocklist")
#parseSource()
#createOutput()
createQuery(sourcepath + sourcefile)



