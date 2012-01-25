#!/usr/local/bin/python

import datetime
import os
import sys 
import simplejson as json

# importable functions 
__all__ = ['fetch_source', 'parse_source']

def fetch_source(source_link, source_file):
    os.system("fetch -o " + source_file + " " + source_link)

def parse_source_and_create_output(source_name, source_file, output_file):
    '''
        Malc0de Parser
    ''' 
    
    update_time = datetime.datetime.now()
    update_time = update_time.strftime("%Y-%m-%d %H:%M")
    
    ip_list = ''

    try:
        source = open(source_file,"r")
        output = open(output_file, "w")
    except Exception, e:
        print 'Exception'
        sys.exit(1)

    # parse the file line by line and create an ip list
    for line in source.readlines()[4:]:
        ip_list += line.split("\n")[0] + ' '

    # JSON Part
    json_dict = {'source_name' : source_name, 'update_time' : update_time, 'ip_list' : ip_list}
    output.write(json.dumps(json_dict))

    output.close()
    source.close()


if __name__ == "__main__":
    print 'calling main'

    # making parameter assignments manually for now.

    source_name = 'Malc0de'
    source_link = 'http://malc0de.com/bl/IP_Blacklist.txt'
    source_file = '/usr/local/nfquery/sources/malc0de/malc0deSource.txt'
    output_file = '/usr/local/nfquery/sources/malc0de/malc0deOutput.txt'

    fetch_source(source_link, source_file)
    parse_source_and_create_output(source_name, source_file, output_file)
    
    
    
    
