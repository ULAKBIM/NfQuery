
import sys

"""
    Utils that are used very frequently.

    * dottedQuadToNum
    * numToDottedQuad
    * query_yes_or_no
"""


def dottedQuadToNum(ip):                                        
    """
        convert decimal dotted quad string to long integer
    """
    
    hexn = ''.join(["%02X" % long(i) for i in ip.split('.')])   
    return long(hexn, 16)                                       
                                                                
# IP address manipulation functions                             
def numToDottedQuad(n):                                         
    """
        convert long int to dotted quad string
    """
                                                                
    d = 256 * 256 * 256                                         
    q = []                                                      
    while d > 0:                                                
        m,n = divmod(n,d)                                       
        q.append(str(m))                                        
        d = d/256                                               
                                                                
    return '.'.join(q)                                          


def query_yes_no(question, default="yes"):
    """
        Ask a yes/no question via raw_input() and return their answer.

        "question" is a string that is presented to the user.
        "default" is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).

        The "answer" return value is one of "yes" or "no".
    """
    valid = {"yes":True,   "y":True,
             "no":False,     "n":False}
    if default == None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "\
                                 "(or 'y' or 'n').\n")

