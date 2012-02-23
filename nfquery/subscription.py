#!/usr/local/bin/python


import nfquery
from logger import createLogger
from defaults import defaults
from models import Source, Subscription, List

import logging
import sys
 

def createSubscriptionTypes(store):
    slogger = createLogger('SubscriptionGenerator')
    slogger.debug('In %s' % sys._getframe().f_code.co_name)
    #store = get_store()
    '''
        We have 2 different subscription types.
        
        1) Source -> example : "Amada,Malc0de,DFN-Honeypot,ABC-NREN_Special_Source"
        2) List Type -> example : "Botnet,Malware,Honeypot Output, Special Source Output"
        
        These subscription types are inserted into subscription table
        according to the condition of "if that subscription type have queries" 
        in query table. "createSubscriptions" function fills the subscription 
        table by inserting these subscription types. 

		!!!!!! SUBSCRIPTION_TAGS NE OLACAK !!!!!!!!

    '''

    # 1) Source Name
    subscription_type=1
    source_name_list = store.find(Source.source_name)
    source_name_list.group_by(Source.source_name)
    for source_name in source_name_list:
        subscription = store.find(Subscription.subscription_id, Subscription.subscription_name == '%s' % (source_name))
        if subscription.count < 1:
            subscription = Subscription()
            subscription.subscription_type = subscription_type
            subscription.subscription_name = source_name
            store.add(subscription)

    # 2) List Type
    subscription_type=2
    list_type_list = store.find(List.list_type)
    list_type_list.group_by(List.list_type)
    for list_type in list_type_list:
        subscription = store.find(Subscription.subscription_id, Subscription.subscription_name == '%s' % (list_type))
        if subscription.count < 1:
            subscription = Subscription()
            subscription.subscription_type = subscription_type
            subscription.subscription_name = list_type
            store.add(subscription)

    store.commit()
    slogger.debug('Subscription types are created')





