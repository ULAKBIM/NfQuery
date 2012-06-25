#!/usr/local/bin/python

# Malware Database (AMaDa) :: AMaDa Blocklist Parser

import time
import os
import sys 
import simplejson as json

# importable functions 
__all__ = ['parse_source']

def parse_source_and_create_output(source_name, source_file, output_type, output_file):
    '''
        Honeypot Source Parser
    '''
    update_time = time.strftime('%Y-%m-%d %H:%M')

    try:
        source = open(source_file, "r")
        outputfile = open(output_file, "w")
    except Exception, e:
        print 'Exception'
        print e
        sys.exit(1)

    expr_list = []
    # parse the file line by line
    # for each line we want another query,
    # so create json dump for each ip:port-ip:port couple
    for line in source.readlines()[2:]:
        #data = line.split("\n")[0]
        #ip,port = data.split(':')
        statement = line.split("\n")[0]
        left, right = statement.split('-')
        src_ip, src_port = left.split(':')
        dst_ip, dst_port = right.split(':')
        expr_list.append({'src_ip' : src_ip, 'src_port': src_port, 'dst_ip' : dst_ip, 'dst_port' : dst_port})

    # JSON
    output = [ 
               {
                'source_name' : source_name,
                'date' : update_time,
                'mandatory_keys' : ['src_ip', 'dst_port'],
                'expr_list' : expr_list 
               } 
             ]

    #print json_dict
    outputfile.write(json.dumps(output, indent=4))
    outputfile.close()
    source.close()


if __name__ == "__main__":
    print 'calling main'

    # making parameter assignments manually for now.

    source_name = 'DFN-Honeypot'
    source_dir  = os.path.dirname(__file__)
    print source_dir
    source_file = source_dir + '/honeypotSource.txt'
    output_type  = 3
    output_file = source_dir + '/honeypotOutput.txt'
    
    #fetch_source(source_link, source_file)
    try:
        parse_source_and_create_output(source_name, source_file, output_type, output_file)
    except Exception,e:
        print e


