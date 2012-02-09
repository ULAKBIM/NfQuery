#!/usr/local/bin/python 


from query import query
import sys

def create_query(source_name, output_type, output, creation_time):
    '''
        API function for parsers to insert query information into database.

        Keyword arguments:                            
        :param source_name   -- Should be string.
                             -- example : 'Amada'

        :param output_type   -- Output type could be on of the three types : Ip, Domain or Port. And we use numbers to 
                             -- indicate each type  ;  1=IP, 2=Domain and 3=Port. 
                             -- example : 1

        :param output        -- Output is a string which consists of splitted ips,ports or domain with a space character as shown below.
                             -- example for ip     : '12.34.22.2 87.55.6.77 192.168.2.1 8.8.8.8' 
                             -- example for domain : 'element-setup.ru/w.php?f=25&e=6 bgehwce.luyfjr.info/catalog.php?rio=1b3b3ebb1e3081a9 ooqfoxw.lyutfy.info/content/score.swf'
                             -- example for port   : '88 90 35 37 54 24 22 1980 990 774' 

        :param creation_time -- Creation time is read from the source, if source does not provide it is calculated as the time of Query Server.


    '''
    myquery = query(source_name, output_type, output, creation_time)
    result = myquery.insert_query()
    return result
    #myquery.print_content()
