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

# Malware Database (AMaDa) :: AMaDa Blocklist Parser

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
     Amada gives information in two columns like that 
     ------------------------------------------------ 
     amada.output file
     ------------------------------------------------ 
     AMaDa IP Domain Blocklist                        
     Provided by abuse.ch Malware Database (AMaDa)    
     ~ http://amada.abuse.ch                          
                                                      
     IP address | Malware name                        
     109.235.251.49 # Fake-AV                         
     109.235.251.51 # Fake-AV                         
     ------------------------------------------------ 
     so parser parses the file after the 5th line
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
    for line in source.readlines()[5:]:
        ip = line.split(" ")[0]
        expr_list.append({'src_ip' :  ip})

    # JSON
    json_dict = [
                 {
                  'source_name' : source_name,
                  'date' : update_time,
                  'mandatory_keys' : ['src_ip'],
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
    #fetch_source(source_link, source_file)
    #parse_source_and_create_output(source_name, source_file, output_type, output_file)
    
    source_name = 'Amada'
    source_link = 'http://amada.abuse.ch/blocklist.php?download=ipblocklist'
    source_file = '/home/serdar/workspace/test/sources/amada/amadaSource.txt'
    output_type  = 1
    output_file = '/home/serdar/workspace/test/sources/amada/amadaOutput.txt'
    
    #fetch_source(source_link, source_file)
    parse_source_and_create_output(source_name, source_file, output_type, output_file)

