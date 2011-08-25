#!/usr/local/bin/python

import MySQLdb
import sys
import re

# Open database connection
db = MySQLdb.connect("localhost","nfquery","nf1!","ulaknet")
# prepare a cursor object using cursor() method
cursor = db.cursor()

# get node information
get_node_information="SELECT id,short_name,long_name FROM Nodes"
Node={}
cursor.execute(get_node_information)
rows=cursor.fetchall()
output=open("outputs/UcBilgileri","w")


head="%-*s%*s"
column1_width=40
column2_width=15
output.write(head % (column1_width, "Uc", column2_width ,"Network Bilgisi\n"))
for row in rows:
    Node["id"]=row[0] 
    Node["shortname"]=row[1] 
    Node["longname"]=row[2] 
    # get node block ips
    get_block_id_info="SELECT block_id FROM Nodes_Blocks WHERE node_id=" + str(Node["id"]);
    cursor.execute(get_block_id_info)
    blockids=cursor.fetchall()
    try:
        blockids=[map(int,block) for block in blockids if block is not None]
    except:
        continue
    for blockid in re.findall(r'\d+', str(blockids)):
        get_ip_block_info="SELECT * FROM Ip_Blocks WHERE id=" + blockid;
        cursor.execute(get_ip_block_info)
        ips=cursor.fetchall()
        for ip in ips:
            #print ip[1], ip[2], ip[3], ip[4]
            network_count=(ip[4]-ip[3]+1)/256
            network=""
            if network_count == 256:
                network=ip[1] + "/16"
            else:
                block=ip[1].split(".")
                for i in range(0,network_count):
                    network+=block[0] + "." + block[1] + "." + str(int(block[2])+i) + "." + block[3] + "/24 "
            output.write(head % (column1_width, Node["longname"], column2_width, (network + "\n")))
            print Node["longname"] + " " + network + "\n"



output.close()
cursor.close()
# disconnect from server
db.close()

