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

import sys
import socket
import struct


def addressInNetwork(ip, net):
    ipaddr = int(''.join([ '%02x' % int(x) for x in ip.split('.') ]), 16)
    netstr, bits = net.split('/')
    netaddr = int(''.join([ '%02x' % int(x) for x in netstr.split('.') ]), 16)
    mask = (0xffffffff << (32 - int(bits))) & 0xffffffff
    return (ipaddr & mask) == (netaddr & mask)


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


def ask_yes_no(question, default="yes"):
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


def is_valid_ipv4_address(address):
    try:
        addr= socket.inet_pton(socket.AF_INET, address)
    except AttributeError: # no inet_pton here, sorry
        try:
            addr= socket.inet_aton(address)
        except socket.error:
            return False
        return address.count('.') == 3
    except socket.error: # not a valid address
        return False

    return True


def is_valid_ipv6_address(address):
    try:
        addr= socket.inet_pton(socket.AF_INET6, address)
    except socket.error: # not a valid address
        return False
    return True


def is_valid_proto(proto):
    if proto == 'tcp' or proto == 'udp':
        return True
    return False 


def is_valid_protocol_version(protocol_version):
    #if proto == 'ipv4' or proto == 'ipv6':
    if proto == 'ipv4':
        return True
    return False 


def is_valid_tos(tos):
    if 0 < tos < 255:
        return True
    return False


def is_valid_flags(flags):
    _flags = ['A', 'S', 'F', 'R', 'P', 'U', 'X']
    if flags in _flags:
        return True
    return False


def is_valid_scale(scale):
    _scale = ['k', 'm', 'g']
    if scale in _scale:
        return True
    return False

        








