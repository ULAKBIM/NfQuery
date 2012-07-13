#!/usr/bin/python
from SOAPpy import SOAPProxy
import json
from IPy import IP
import netaddr
import os
from config import Config, ConfigError

from_node_ifdesc_dir = "/from_node_ifdesc"
to_node_ifdesc_dir = "/to_node_ifdesc"
from_node_ip_dir = "/from_node_ip"
to_node_ip_dir = "/to_node_ip"
node_to_node_dir = "/node_to_node"


def parseConfig(conf_file):
    global config
    try:
        config = Config(conf_file)
	return config
    except ConfigError, e:
        print("Please check configuration file syntax")
        print("%s" % e)
	sys.exit(1)





def createdirectory(node_to_node_dir,from_node_ifdesc_dir,from_node_ip_dir,to_node_ifdesc_dir,to_node_ip_dir,filter_dir):
    if not os.path.exists(filter_dir):
    	os.mkdir(filter_dir)
    if not os.path.exists(node_to_node_dir):
    	os.mkdir(node_to_node_dir)
    if not os.path.exists(from_node_ifdesc_dir):
    	os.mkdir(from_node_ifdesc_dir)
    if not os.path.exists(from_node_ip_dir):
    	os.mkdir(from_node_ip_dir)
    if not os.path.exists(to_node_ifdesc_dir):
    	os.mkdir(to_node_ifdesc_dir)
    if not os.path.exists(to_node_ip_dir):
    	os.mkdir(to_node_ip_dir)


def connectWS(location,uri):
    global block
    global result
    try:
    	p = SOAPProxy(location, uri)
    	result = p.wsGetMainLinksByInstId()
    	ips = p.wsGetIPByInstId()
    
    except:
    	print "can not connect"
    	print "baska bahara kaldi"
    	exit(0)
    result = json.loads(result)
    resultip = json.loads(ips)
    
    
    block = {}
    global myid
    for node in resultip:
        block2 = []
        for node2 in resultip[node]:
            myid = node2["ip_inst_id"]	
            if node2["ip_type"]==4:
    	        if node2["ip_prefixlen"] ==None:
                    ip_list = list(netaddr.iter_iprange(str(node2["ip_begin"]),str(node2["ip_end"])))
    		    ip_list = netaddr.cidr_merge(ip_list)
    		    for i in ip_list:
    		        block2.append( str(i))
                else:
    		    ip_range = str(node2["ip_begin"]+"-"+node2["ip_end"])
    		    block2.append( str(IP(ip_range)))
        block[myid]=block2





def is_index(liste,index):
    if index in liste.keys():
        return True
    else:
        return False	

def create_ifdesc_dstnet(ifdesc,inst_id):
    ip_list = block[inst_id]
    f = " or dst net ".join(ip_list)
    filterr = "in if " + str(ifdesc) + " and (dst net "+f +")"
    return filterr

def create_srcnet_dstnet(inst_id1,inst_id2):
    ip_list1 = block[inst_id1]
    ip_list2 = block[inst_id2]
    f1 = " or src net ".join(ip_list1)
    f2 = " or dst net ".join(ip_list2)
    filterr = " (src net "+ f1+ ") and  dst net (" + f2 + ")"
    return filterr


def create_ifdesc_ifdesc(ifdesc1,ifdesc2):
    filterr = "in if " + str(ifdesc1) + " and out if "+str(ifdesc2)
    return filterr

def create_srcnet_ifdesc(inst_id,if_index):
    ip_list = block[inst_id]
    f = " or dst net".join(ip_list)
    filterr = " (src net "+ f+ ") and  out if " + str(if_index)
    return filterr

def from_node_to_node():
    for element1 in result:
        for node1 in result[element1]:
            for element2 in result: 
                for node2 in result[element2]:
    	            file_name = node_to_node_dir+"/"+result[element1][node1]["inst_code"]+"_"+result[element2][node2]["inst_code"]
                    if result[element1][node1]["router_name"]==result[element2][node2]["router_name"] and result[element1][node1]["link_id"]!=result[element2][node2]["link_id"]:
                        if (result[element2][node2]["router_ifindex"]!=None):
                            if len(result[element1])>1:			
                                if is_index(block,result[element2][node2]["inst_id"]):
                                    filterr = create_srcnet_ifdesc(result[element2][node2]["inst_id"],result[element2][node2]["router_ifindex"])
                                    filee = open(file_name,"w")
                                    filee.write(filterr)
                                    filee.close()	
                            else:
                                if(result[element1][node1]["router_ifindex"]!=None):	
                                    filterr = create_ifdesc_ifdesc(result[element1][node1]["router_ifindex"],result[element2][node2]["router_ifindex"])
                                    filee = open(file_name,"w")
                                    filee.write(filterr)
                                    filee.close()	
            	    else:
                        if result[element1][node1]["link_id"]!=result[element2][node2]["link_id"]:
                            if len(result[element1])>1:
                                if is_index(block,result[element1][node1]["inst_id"]) and is_index(block,result[element2][node2]["inst_id"]) :
                                    filterr = create_srcnet_dstnet(result[element1][node1]["inst_id"],result[element2][node2]["inst_id"])
                                    filee=open(file_name,"w")
                                    filee.write(filterr)
                                    filee.close()
                            else:
                                if is_index(block,result[element2][node2]["inst_id"]):
                                    filterr = create_ifdesc_dstnet(result[element1][node1]["router_ifindex"],result[element2][node2]["inst_id"])
                                    filee = open(file_name,"w")
                                    filee.write(filterr)
                                    filee.close()

def from_node_ifdesc(name=None):
    if not name:
        for i in result:
            for node1 in result[i]:
	        if result[i][node1]["router_ifindex"] != None:
		    if_desc = result[i][node1]["router_ifindex"]
		    file_name = from_node_ifdesc_dir + "/from_" + result[i][node1]["inst_code"]  
		    filter = "in if " + result[i][node1]["router_ifindex"]
		    filee = open(file_name,"w")
		    filee.write(filter)
		    filee.close()
    else:
        for i in result:
	    for node1 in result[i]:
	    	if result[i][node1]["inst_code"] == name:
	            if result[i][node1]["router_ifindex"] != None:
	                if_desc = result[i][node1]["router_ifindex"]
	                filter = "in if " + result[i][node1]["router_ifindex"]
      			return filter

def from_node_ip(name=None):
    if not name:
        for i in result:
            for node1 in result[i]:
	        if is_index(block,result[i][node1]["inst_id"]):
                    ip_list = block[result[i][node1]["inst_id"]]
                    f = " src net ".join(ip_list)
		    file_name = from_node_ip_dir + "/from_" + result[i][node1]["inst_code"]  
		    filter = "src net " + f
		    filee = open(file_name,"w")
		    filee.write(filter)
		    filee.close()
    else:
        for i in result:
            for node1 in result[i]:
	        if result[i][node1]["inst_code"] == name:
	            if is_index(block,result[i][node1]["inst_id"]):
                        ip_list = block[result[i][node1]["inst_id"]]
                        f = " src net ".join(ip_list)
		        filter = "src net " + f
                        return filter
		    else:
		        return ""

def to_node_ifdesc(name=None):
    if not name:
        for i in result:
	    for node1 in result[i]:
	        if result[i][node1]["router_ifindex"] != None:
	            if_desc = result[i][node1]["router_ifindex"]
	            file_name = to_node_ifdesc_dir + "/to_" + result[i][node1]["inst_code"]
	            filter = "out if " + result[i][node1]["router_ifindex"]
	            filee = open(file_name,"w")
	            filee.write(filter)
	            filee.close()
    else:
        for i in result:
	    for node1 in result[i]:
	        if result[i][node1]["inst_code"] == name:
		    if result[i][node1]["router_ifindex"] != None:
		        if_desc = result[i][node1]["router_ifindex"]
			filter = "out if " + result[i][node1]["router_ifindex"]
			return filter



def to_node_ip(name=None):
    if not name:
        for i in result:
            for node1 in result[i]:
	        if is_index(block,result[i][node1]["inst_id"]):
                    ip_list = block[result[i][node1]["inst_id"]]
                    f = " dst net ".join(ip_list)
		    file_name = to_node_ip_dir + "/to_" + result[i][node1]["inst_code"]  
		    filter = "dst net " + f
		    filee = open(file_name,"w")
		    filee.write(filter)
		    filee.close()
    else:
        for i in result:
            for node1 in result[i]:
	        if result[i][node1]["inst_code"] == name:
	            if is_index(block,result[i][node1]["inst_id"]):
                        ip_list = block[result[i][node1]["inst_id"]]
                        f = " dst net ".join(ip_list)
		        filter = "dst net " + f
                        return filter
		    else:
		        return ""


if __name__ == "__main__":
    config = parseConfig(os.getcwd()+"/matrice.conf")
    location = config.location.wslocation
    uri = config.location.uri
    connectWS(location,uri)
    from_node_ifdesc_dir = config.directory.filter_directory+"/from_node_ifdesc"
    to_node_ifdesc_dir =config.directory.filter_directory + "/to_node_ifdesc"
    from_node_ip_dir = config.directory.filter_directory +"/from_node_ip"
    to_node_ip_dir = config.directory.filter_directory + "/to_node_ip"
    node_to_node_dir = config.directory.filter_directory + "/node_to_node"
    filter_dir = config.directory.filter_directory
    createdirectory(node_to_node_dir,from_node_ifdesc_dir,from_node_ip_dir,to_node_ifdesc_dir,to_node_ip_dir,filter_dir)
    from_node_to_node()
    from_node_ifdesc()
    from_node_ip()
    to_node_ifdesc()
    to_node_ip()
