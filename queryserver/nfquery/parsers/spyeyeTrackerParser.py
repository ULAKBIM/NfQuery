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

# abuse.ch SpyEye IP blocklist 

from datetime import date
import os

def sourceFetch():
    SpyEyeTracker_bl_source = "https://spyeyetracker.abuse.ch/blocklist.php?download=ipblocklist  "
    os.system("fetch  " + SpyEyeTracker_bl_source)
    os.system("mv blocklist.php* " + sourcepath + "blocklist")


def sourceParse():    
    blfile=open(sourcepath + "blocklist","r")
    blocklist[mal_name]=""
    for i in blfile.readlines()[6:]:
        mal_ipaddr = i.split("\n")[0]
        blocklist[mal_name]=blocklist[mal_name] + " " + mal_ipaddr 

def createOutput():
    today=date.today().isoformat()
    source="SpyEyeTracker"
    port="-"
    MalOutput=open(outputpath + "MalOutput.SpyEyeTracker","w")
    alignment="%-*s%-*s%-*s%-*s%*s"
    column1_width=20
    column2_width=20
    column3_width=15
    column4_width=15
    column5_width=15
    MalOutput.write(alignment % (column1_width, "MalType", column2_width, "MalIPaddress", column3_width, "Port", column4_width, "Source", column5_width, "Date\n"))
    for mal_name, mal_ipaddr in blocklist.items():
        for each_ip in mal_ipaddr.split(" ")[1:]:
            MalOutput.write( alignment % (column1_width, mal_name, column2_width, each_ip, column3_width, port, column4_width, source, column5_width, today+"\n"))
    MalOutput.close()



#sourceFetch()
sourceParse()
createOutput()












