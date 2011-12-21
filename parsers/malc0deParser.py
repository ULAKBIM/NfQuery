#!/usr/local/bin/python

# Malware Database (AMaDa) :: AMaDa Blocklist Parser

from datetime import date
import os
import sys 

# nfquery modules
from querygenerator import create_query

sys.path.append('..')

__all__ = ['fetch_source', 'parse_source']

def fetch_source(source_link, source_file):
    print "fetch  -o " + source_file + " " + source_link
    os.system("fetch  -o " + source_file + " " + source_link)

def parse_source(source_name, source_link, source_file):
    '''
        This file will be automatically updated daily and populated with the last 30 days of malicious IP addresses.'
        Last updated 2011-12-20  
    '''
    today = date.today().isoformat()
    sourcefile=open(source_file, "r")
    blacklist = {}
    # Manual ? 
    mal_name = "DNSBlackhole"
    blacklist[mal_name] = ""
    for i in sourcefile.readlines()[4:]:
        mal_ipaddr = i.split("\n")[0]
        blacklist[mal_name]=blacklist[mal_name] + " " + mal_ipaddr 
    create_query(source_name, source_link, mal_name, "", 1, blacklist[mal_name], today)

# CHECK IT # def createOutput():
# CHECK IT #     today=date.today().isoformat()
# CHECK IT #     source="malc0de DNS Blackhole"
# CHECK IT #     port="-"
# CHECK IT #     MalOutput=open(outputpath + "MalOutput.malc0de","w")
# CHECK IT #     alignment="%-*s%-*s%-*s%-*s%*s"
# CHECK IT #     column1_width=20
# CHECK IT #     column2_width=20
# CHECK IT #     column3_width=20
# CHECK IT #     column4_width=20
# CHECK IT #     column5_width=20
# CHECK IT #     MalOutput.write(alignment % (column1_width, "MalType", column2_width, "MalIPaddress", column3_width, "Port", column4_width, "Source", column5_width, "Date\n"))
# CHECK IT #     for mal_name, mal_ipaddr in blocklist.items():
# CHECK IT #         for each_ip in mal_ipaddr.split(" ")[1:]:
# CHECK IT #             MalOutput.write( alignment % (column1_width, mal_name, column2_width, each_ip, column3_width, port, column4_width, source, column5_width, today+"\n"))
# CHECK IT #     MalOutput.close()


def main():
    ''' 
        source_name should be registered to Query Server before using its parser.
    '''
    fetch_source(source_link, source_file)
    parse_source(source_file)



if __name__ == "__main__":
    print 'calling main'
    main()












