#!/usr/local/bin/python

# Malware Database (AMaDa) :: AMaDa Blocklist Parser

import datetime
import os
import sys 
import simplejson as json

# importable functions 
__all__ = ['parse_source']

def parse_source_and_create_output(source_name, source_file, output_type, output_file):
    '''
        Test Top Ten IPPort Source Parser
    '''
    update_time = datetime.datetime.now()
    update_time = update_time.strftime("%Y-%m-%d %H:%M")

    output = ''

    try:
        source = open(source_file, "r")
        outputfile = open(output_file, "w")
    except Exception, e:
        print 'Exception'
        sys.exit(1)

    expr_list = []
    # parse the file line by line
	# for each line we want another query,
	# so create json dump for each ip:port-ip:port couple
    for line in source.readlines()[2:]:
        #data = line.split("\n")[0]
        #ip,port = data.split(':')
        statement = line.split("\n")[0]
        if '-' in statement:
            left, right = statement.split('-')
            src_ip, src_port = left.split(':')
            dst_ip, dst_port = right.split(':')
            expr_list.append({'src_ip' : src_ip, 'src_port' : src_port, 'dst_ip' : dst_ip, 'dst_port' : dst_port})
        else:
            src_ip, src_port = statement.split(':')
            expr_list.append({'src_ip' : src_ip, 'src_port' : src_port})

    # JSON
    json_dict = {'source_name' : source_name,
                 'update_time' : update_time,
                 'mandatory_fields' : ['src_ip', 'dst_port'],
                 'expr_list' : expr_list 
                }

    print json_dict
    outputfile.write(json.dumps(json_dict, indent=4))
    outputfile.close()
    source.close()


if __name__ == "__main__":
    print 'calling main'

    # making parameter assignments manually for now.

    #source_name = 'Amada'
    #source_link = 'http://amada.abuse.ch/blocklist.php?download=ipblocklist'
    #source_file = '/usr/local/nfquery/sources/amada/amadaSource.txt'
    #output_type  = 1 
    #output_file = '/usr/local/nfquery/sources/amada/amadaOutput.txt'
    #
    #fetch_source(source_link, source_file)
    #parse_source_and_create_output(source_name, source_file, output_type, output_file)
    
    source_name = 'TestIPPort'
    source_file = '/home/serdar/workspace/test/sources/ipport/IPPortSource.txt'
    output_type  = 3
    output_file = '/home/serdar/workspace/test/sources/ipport/IPPortOutput.txt'
    
    #fetch_source(source_link, source_file)
    parse_source_and_create_output(source_name, source_file, output_type, output_file)


