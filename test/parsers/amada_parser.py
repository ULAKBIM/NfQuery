#!/usr/local/bin/python

# Malware Database (AMaDa) :: AMaDa Blocklist Parser

import os

nfquery = "/usr/local/nfquery/"
sourcepath = nfquery + "sources/amada/"
amada_bl_source = "http://amada.abuse.ch/blocklist.php?download=ipblocklist  "

def fetch_and_parse():
    #os.system("fetch  " + amada_bl_source)
    #os.system("mv block* " + sourcepath + "blocklist")
    
    blfile=open(sourcepath + "blocklist","r")
    blocklist={}
    linesCounter = 1
    for i in blfile.readlines()[:10]:
        if linesCounter > 5:
            #for i in 
            mal_ipaddr=i.split(" ")[0]
            mal_name=i.split(" ")[2].split("\n")[0]
            blocklist{ 
            #blocklist[mal_name]=mal_ipaddr
        
        #print mal_ipaddr + "  " + mal_name
        
        linesCounter += 1
    print blocklist 
    


fetch_and_parse()
