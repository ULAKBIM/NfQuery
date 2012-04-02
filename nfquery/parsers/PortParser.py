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
        Test Top Ten Port Source Parser
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

    # parse the file line by line and create an ip list
    expr_list = []
    for line in source.readlines()[1:]:
        port = line.split("\n")[0]
        expr_list.append({'src_port' :  port})

    # JSON
    json_dict = [
                 {
                  'source_name' : source_name,
                  'update_time' : update_time,
                  'mandatory_fields' : ['src_port'],
                  'expr_list' : expr_list
                 }
                ]
    #print json_dict
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
    
    source_name = 'TestPort'
    source_file = '/home/serdar/workspace/test/sources/port/PortSource.txt'
    output_type  = 2
    output_file = '/home/serdar/workspace/test/sources/port/PortOutput.txt'
    
    #fetch_source(source_link, source_file)
    parse_source_and_create_output(source_name, source_file, output_type, output_file)


