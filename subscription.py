#!/usr/local/bin/python


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

    def createSubscriptionTypes(self):
        '''
            We have 4 different subscription types.
            
            1) Source -> example : "Amada"
            2) Source + Threat Type -> example : "Amada,Botnet"
            3) Source + Threat Type + Threat Name -> example : "Amada,Botnet,Spyeye"
            4) Threat Type -> example : "Botnet"
            5) Threat Name -> example : "Spyeye"
            
            These subscription types are inserted into subscription table
            according to the condition of "if that subscription type have queries" 
            in query table.  Subscription types are consist of the permutation of 
            source_name, threat_type and threat_name fields in the database tables 
            "threat" and "source". So createSubscriptions function fills the subscription 
            table by inserting these subscription types. It should be run in a time 
            period for the new subscription types to be added to the subscription table. 
        '''

        # insert subscription types that have queries

        # 1) source name
        # select source_name from source where source_id IN(select source_id from query group by source_id) group by source_name;

        # 2) source name + threat_type
        # select source_name from source where source_id IN(select source_id from query group by source_id);
        # select source_id from query group by source_id;
        # fetchall
        # for i in fetchall
        #    select threat_type from threat where threat_id IN(select threat_id from query where source_id=i group by threat_id);
        #    fetchall
        #    for j in fetchall
        #       source_name,threat_type

        # 3) source_name + threat_type + threat_name
        # 
        # select source_name from source where source_id IN(select source_id from query group by source_id);
        # fetchall
        # for i in fetchall
        #    select threat_type from threat where threat_id IN(select threat_id from query where source_id=i group by threat_id) group by threat_type;
        #    fetchall
        #    for j in fetchall
        #       select threat_name from threat where threat_type=j
        #       source_name,threat_type,threat_name
        
        # 4) threat type
        # select threat_type from threat where threat_id IN(select threat_id from query group by threat_id) group by threat_type;

        # 5) threat name 
        # select threat_name from threat where threat_id IN(select threat_id from query group by threat_id) and threat_name is not null  group by threat_name ;


    def generateJSONPacketsFromSubscription(self):
        pass

