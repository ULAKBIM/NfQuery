#!/usr/local/bin/python

import datetime
import os
import sys 
import simplejson as json

# importable functions 
__all__ = ['fetch_source', 'parse_source']

def fetch_source(source_link, source_file):
    os.system("fetch -o " + source_file + " " + source_link)

def parse_source_and_create_output(source_name, source_file, output_type, output_file):
    '''
        Malc0de Parser
    ''' 
    
    update_time = datetime.datetime.now()
    update_time = update_time.strftime("%Y-%m-%d %H:%M")
    
    output = ''

    try:
        source = open(source_file,"r")
        outputfile = open(output_file, "w")
    except Exception, e:
        print 'Exception'
        sys.exit(1)

    # parse the file line by line and create an ip list
    for line in source.readlines()[4:]:
        output += line.split("\n")[0] + ' '

    # JSON Part
    json_dict = {'source_name' : source_name, 'update_time' : update_time, 'output_type' : output_type, 'output' : output, 'tos':123, 'packets':1450, 'protocol':'tcp', 'protocol_version':'ipv6', 'bytes':12345}
    #json_dict = {'source_name' : source_name, 'update_time' : update_time, 'output_type' : output_type, 'output' : output}
    outputfile.write(json.dumps(json_dict))

    outputfile.close()
    source.close()


if __name__ == "__main__":
    print 'calling main'

    # making parameter assignments manually for now.


    #source_link = 'http://malc0de.com/bl/IP_Blacklist.txt'
    #source_file = '/usr/local/nfquery/sources/malc0de/malc0deSource.txt'
    #output_type = 1 # Ip list
    #output_file = '/usr/local/nfquery/sources/malc0de/malc0deOutput.txt'

    #fetch_source(source_link, source_file)
    #parse_source_and_create_output(source_name, source_file, output_type, output_file)
    
    source_name = 'malc0de'
    source_link = 'http://malc0de.com/bl/IP_Blacklist.txt'
    source_file = '/home/serdar/workspace/test/sources/malc0de/malc0deSource.txt'
    output_type = 1 # Ip list
    output_file = '/home/serdar/workspace/test/sources/malc0de/malc0deOutput.txt'

    #fetch_source(source_link, source_file)
    parse_source_and_create_output(source_name, source_file, output_type, output_file)

    
    
