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

#import sys
#import os
#from distutils.core import setup

from setuptools import setup

setup( 
       name='nfquery',
       version='1.0',
       author = "Serdar Yigit",
       author_email = "syigitisk@gmail.com",
       description = ("A thing"),
       license = "BSD",
       keywords = "test setup",
       #url = "http://packages.python.org/an_example_pypi_project",
	   packages=['nfquery'],
       scripts=['bin/nfqueryd'],
	   zip_safe = False,
	   #install_requires = ['MySQLdb',],
       data_files = [
             ('/etc/',['/home/serhat/nfquery/cfg/nfquery.conf'])
       		#('/etc/',['/home/ahmetcan/projects/conf/cfg/nfquery.conf'])
            #    ('/etc/',['/home/hamza/nfquery/cfg/nfquery.conf'])
       ],
	   #entry_points = {
	   # 	'console_scripts': [
	   # 		#'nfquery = nfquery.nfquery:go',
       #         'nfqueryd = bin.nfqueryd'
	   # 	]	
	   #	},
     )

#import os
#os.system('mv /usr/local/bin/nfqueryd /usr/local/bin/Nfquery')

#os.chown('/usr/bin/nfquery.py','serdar','serdar')
#os.chown('/etc/nfquery.conf','serdar','serdar')

