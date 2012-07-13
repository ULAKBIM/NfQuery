from SOAPpy import SOAPProxy
import json
import os,sys
import _mysql
from config import Config, ConfigError
from  multiprocessing import Pool
import datetime

nfdump_path = "/usr/bin/nfdump"


config_file = os.getcwd()+"/matrice.conf"

print config_file



def router(location,uri):
    global router
    try:
        p = SOAPProxy(location, uri)
        result = p.wsGetMainLinksByInstId()
    	
    except:
        print "can not connect"
        print "baska bahara kaldi"
        exit(0)
    result = json.loads(result)
    router = {}
    istanbul = []
    izmir = []
    ankara = []
    konya = []
    for element in result:
        for node in result[element]:
    
            if result[element][node]['router_man_ip'] == "193.140.0.5":
                if result[element][node]['inst_code'] not in istanbul:
                    istanbul.append(result[element][node]['inst_code'])
    
            elif result[element][node]['router_man_ip'] == "193.140.0.6":
    	        if result[element][node]['inst_code'] not in izmir:
                    izmir.append(result[element][node]['inst_code'])
    
            elif result[element][node]['router_man_ip'] == "193.140.0.4":
                if result[element][node]['inst_code'] not in ankara:
    	            ankara.append(result[element][node]['inst_code'])
	    elif result[element][node]['router_man_ip'] == "193.140.0.7":
	        if result[element][node]['inst_code'] not in konya:
		    konya.append(result[element][node]['inst_code'])
    router={'istanbul':istanbul,'ankara':ankara,'izmir':izmir,'konya':konya}

def parseConfig(conf_file):
    try:
        config = Config(conf_file)
        return config
    except ConfigError, e:
        print("Please check configuration file syntax")
        print("%s" % e)
        sys.exit(1)



def connectdb(config):
    try:
        db=_mysql.connect(config.database.host,config.database.user,config.database.password,config.database.database)
	return db
    except:
        print "can not connect to mysql!"

def insert_table(db,fromm, to, date, flow, byte, packet,flow_percent,byte_percent,packet_percent):
    query = "INSERT INTO node_to_node (id, fromm, too, date, flow, flow_percent, byte, byte_percent, packet, packet_percent)\
    	    VALUES (NULL,'" + fromm + "','" + to + "','" + date + "','" + flow  + "'," + "NULL,'" + byte + "'," + "NULL,'" + packet + "'," + "NULL" + ");"
    #print query
    db.query(query)

def find_router(inst_code):
    for i in router:
        for j in router[i]:
	    if j==inst_code:
	        return i


def get_filter(fromm,to):
    file_name = fromm+"/"+fromm + "_" + to
    file = open(filter_dir+"/"+file_name,"r")
    filter = file.readline()
    file.close()
    return filter

def calistir(fromm,to,start_time,end_time):
#    print "calitir_basladi"
    router_name = find_router(fromm)
    now = datetime.datetime.now()
    date_dir=str(now).split(" ")[0]
    flow_sub_dir = flow_dir + "/" + router_name
    if router_name=='izmir':
    	flow_sub_dir = flow_sub_dir + "huawaei"
    else:
        flow_sub_dir = flow_sub_dir + "huawei"
    flow_sub_dir = flow_sub_dir +  "/" + date_dir 
    if os.path.exists(flow_sub_dir):
        flowFileList=os.listdir(flow_sub_dir)
        
        filter = get_filter(fromm,to)
        command = nfdump_path + " -I -M " + flow_sub_dir + " -R nfcapd." + start_time + ":nfcapd." + end_time + " '" + filter + "'"
	#print command
	#print fromm+" " +to

        result = os.popen(command).read()
        D= result.rstrip("\n")
        liste = result.split("\n")
        liste.pop()
        my_result = {}
        date = start_time[:8]
        for i in liste:
            my_result[ i.split(":")[0]]=i.split(":")[1]
        insert_table(database,fromm,to,date,my_result['Flows'],my_result['Bytes'],my_result['Packets'],"3","3","3")
        #insert_table(database,'odtu','ulakbim','201207','','','','','','')
def is_finish(liste):
    for i in liste:
       if i.is_alive()==True:
           return False
    return True


if __name__ == "__main__":
    global database
    global flow_dir        
    global filter_dir
    config = parseConfig(config_file)
    location = config.location.wslocation
    uri = config.location.uri
    flow_dir = config.directory.flow_directory
    filter_dir = config.directory.filter_directory
    filter_dir = filter_dir + "/node_to_node"
    router(location,uri)
    database = connectdb(config)
    dirList=os.listdir(filter_dir)
    job = []
    pool = Pool(processes=300)
    now = datetime.datetime.now()
    date = "".join(str(now).split(" ")[0].split("-"))
    start_time = date + "1600"
    end_time = date + "1600"
    for i in router:
        for j in router[i]:
            file_name = filter_dir +"/"+j
            g=os.popen("ls "+ file_name + "/" + j + "*").read()
            g=g.rstrip()
#	    print file_name
            for k in g.split("\n"):
                fromm = k.split("/")[-1].split("_")[0]
                to = k.split("/")[-1].split("_")[1]
#		print fromm,to
#    for i in dirList:
#        print i
#        fromm = i.split("_")[0]
#	to = i.split("_")[1]
#	#fromm='odtu'
#	#to='ulakbim'
	    	#print start_time,end_time
                pool.apply_async(calistir, (fromm,to,start_time,end_time))
    pool.close()
    pool.join()
#        p = multiprocessing.Process(target = calistir, args=(fromm,to,))
#	job.append(p)
	#p.start()
#    i=0
#    job2=[]
#    for i in range(1000):
#        job[i].start()
##    while i<len(job):
##       job2.append(job[i:i+1000])
##       i=i+1000
##
##    for i in job2:
##        for j in i:
##	    j.start()
##	break
#    i= job[:200]
#    while is_finish(i) is not True:
#       pass	
#        
#
#	#calistir('odtu','ulakbim','201207111040','201207111050')









