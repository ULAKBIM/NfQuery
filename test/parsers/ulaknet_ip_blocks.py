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
output.write("Uc\t\t\t\t\tNetwork Bilgisi\n")
index=0
for row in rows:
    print row[0], row[1], row[2]
    Node["index"]=index
    index+=index
    Node[("index", "id")]=row[0] 
    Node[("index", "shortname")]=row[1] 
    Node[("index", "longname")]=row[2] 
    # get node block ips
    get_block_id_info="SELECT block_id FROM Nodes_Blocks WHERE node_id=" + str(Node[("index", "id")]);
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
            print ip[1], ip[2]
            output.write(row[1] + "\t\t\t\t\t" + ip[1] + "\t" + ip[2] + "\n")

output.close()
cursor.close()
# disconnect from server
db.close()

