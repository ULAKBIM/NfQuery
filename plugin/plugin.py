#!/usr/local/bin/python


from twisted.internet import reactor
from txjsonrpc.web.jsonrpc import Proxy
from config import Config, ConfigError

import time
import sys

def printValue(value):
    print "Result: %s" % str(value)

def printError(error):
    print 'error', error

def shutDown(data):
    print "Shutting down reactor..."
    reactor.stop()


if __name__ == "__main__":

    configfile = './plugin.conf'

    # Parse Config File
    try:
        config = Config(configfile)
    except ConfigError, e:
        print("Please check configuration file syntax")
        print("%s" % e)
        sys.exit(1)

    print('Parsing configuration file options')

    # here, Check for conf options !! 

    proxy = Proxy('https://127.0.0.1:7777/')
    e = proxy.callRemote('register', config.plugin.organization, config.plugin.adm_name, config.plugin.adm_mail, config.plugin.adm_mail, 
                          config.plugin.adm_publickey_file, config.plugin.prefix_list, config.plugin.plugin_ip)
    e.addCallback(printValue).addErrback(printError).addBoth(shutDown)
    reactor.run()



