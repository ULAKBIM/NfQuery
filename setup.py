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
	   packages=['nfquery', 'nfquery.json_test'],
       scripts=['bin/nfqueryd'],
	   zip_safe = False,
	   #install_requires = ['MySQLdb',],
       data_files = [
       		('/etc/',['cfg/nfquery.conf'])
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

