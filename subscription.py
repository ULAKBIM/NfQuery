#!/usr/local/bin/python

from db import db as database 
#from query import query

#----------------------------------------------------------# 
# Create subscription packets for each subscription        #   
# type.                                                    #   
#                                                          #   
# subscription_type=1 -> Source                            #   
# subscription_type=2 -> Source,Threat_Type                #   
# subscription_type=3 -> Source,Threat_Type,Threat_Name    #   
# subscription_type=4 -> Threat_Type                       #   
# subscription_type=5 -> Threat_Name                       #   
#                                                          #   
#----------------------------------------------------------#  


class subscription():
    def __init__(self, subscription_name, subscription_query_list, subscription_update_time):
        self.subscription_name = subscription_name
        self.subscription_query_list = subscription_query_list
        self.subscription_update_time = subscription_update_time

    def generateThreatSubscription(source_id, threat_id):
        pass
    
    def generateJSONPacketsFromSubscription():
        pass


