# This file is part of NfQuery.  NfQuery is free software: you can
# redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright NfQuery Team Members

#!/usr/local/bin/python

# Malware Database (EMRE) :: AMaDa Blocklist Parser

import time
import os
import sys 
import simplejson as json
from config import Config, ConfigError
import urllib

# importable functions 
__all__ = ['parse_source']

def parse_source_and_create_output(source_name, source_file, output_type, output_file):
    '''
        Test Top Ten IPPort Source Parser
    '''
    update_time = time.strftime('%Y-%m-%d %H:%M')

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
        src_ip, dst_port = statement.split(':')
        expr_list.append({'src_ip' : src_ip, 'dst_port' : dst_port})

    # JSON
    output = [ 
               {
                'source_name' : source_name,
                'date' : update_time,
                'mandatory_keys' : ['src_ip','dst_port'],
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

    #source_name = 'Amada'
    #source_link = 'http://amada.abuse.ch/blocklist.php?download=ipblocklist'
    #source_file = '/usr/local/nfquery/sources/amada/amadaSource.txt'
    #output_type  = 1 
    #output_file = '/usr/local/nfquery/sources/amada/amadaOutput.txt'
    #
    #fetch_source(source_link, source_file)
    #parse_source_and_create_output(source_name, source_file, output_type, output_file)
#    config_file = "/home/hamza/nfquery/cfg/nfquery.conf"
    
    source_dir  = os.path.dirname(__file__)    
    source_name = 'emre'
    source_file = source_dir + '/emreSource.txt'
    output_type  = 3
    output_file = source_dir + '/emreOutput.txt'
    


#    # Parse Config File
#    try:
#        config = Config(config_file)
#    except ConfigError, e:
#        print 'Please check configuration file syntax'
#
#    sources = config.sources
#    for source in sources:
#        if source['source_name'] == 'emre':
#            emre_info = source
#            break
#    emre_url = emre_info['source_link']
#
#    content = urllib.urlopen(emre_url)
#    content = content.readlines()
#    try:
#        source_file = open('/home/hamza/nfquery/NfQuery/nfquery/sources/emre/emreSource.txt', 'w')
#    except Exception, e:
#        print 'Exceptions'
#        sys.exit(1)
#
#    for row in content:
#        source_file.writelines(row)
#    source_file.close()
    #fetch_source(source_link, source_file)
    parse_source_and_create_output(source_name, source_file, output_type, output_file)


