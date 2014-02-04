#!/usr/bin/env python
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

# Palevo Parser

import datetime
import os
import sys 
import simplejson as json
import urllib2
import re

update_time = datetime.datetime.now()
update_time = update_time.strftime("%Y-%m-%d %H:%M")

if len(sys.argv) != 4:
	print "Should be called like\n\t%s SourceName SourceURL OutputFile\n" % sys.argv[0]
	sys.exit(1)

source_name = sys.argv[1]
source_link = sys.argv[2]
output_file = sys.argv[3]

try:
	ofh = open(output_file, "w")
except Exception, e:
	print "OutputFile(%s) cannot be opened for write!" % output_file
	sys.exit(2)

try:
	data = urllib2.urlopen(source_link)
except Exception, e:
	print "Source url: %s cannot be read: %s" % (source_link, str(e))
	ofh.close()
	sys.exit(3)

expr_list = []
for lines in data.readlines():
	lines = lines.lstrip().rstrip("\t\n\r ")
	lines = re.sub(r'\s*(#|//).*', '', lines)
	if (len(lines) == 0):
		continue;
        expr_list.append({'src_ip' :  lines})

json_dict = [
             {
              'source_name' : source_name,
              'date' : update_time,
              'mandatory_keys' : ['src_ip'],
              'expr_list' : expr_list
             }
            ]

ofh.write(json.dumps(json_dict, indent=4))
ofh.close()

