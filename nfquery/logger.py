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

import logging
import sys


__all__ = ['createLogger']

#The background is set with 40 plus the number of the color, and the foreground with 30

#These are the sequences need to get colored ouput
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"

LOGLEVEL = 0

def createLogger(name, console=True):
    # Start Logging Module
    logging.setLoggerClass(ColoredLogger)
    mylogger = logging.getLogger(name)
    mylogger.to_console = console
    mylogger.setLevel(LOGLEVEL)
    return mylogger


def formatter_message(message, use_color = True):
    if use_color:
        message = message.replace("$RESET", RESET_SEQ).replace("$BOLD", BOLD_SEQ)
    else:
        message = message.replace("$RESET", "").replace("$BOLD", "")
    return message


COLORS = {
    'WARNING': 5,  # Magenta
    'INFO': 2,     # Green
    'DEBUG': 6,    # Ocean
    'CRITICAL': 8, # Purple
    'ERROR': 1     # Red
}


class ColoredFormatter(logging.Formatter):
    def __init__(self, msg, use_color = True):
        logging.Formatter.__init__(self, msg, datefmt="%H:%M:%S")
        self.use_color = use_color

    def format(self, record):
        levelname = record.levelname
        if self.use_color and levelname in COLORS:
            levelname_color = COLOR_SEQ % (30 + COLORS[levelname]) + levelname + RESET_SEQ
            record.levelname = levelname_color
        return logging.Formatter.format(self, record)


# Custom logger class with multiple destinations
class ColoredLogger(logging.Logger):
    #FORMAT = "[$BOLD%(name)-s$RESET][%(levelname)-s]  %(message)s (%line : (lineno)d)"
    FORMAT = "%(asctime)s [$BOLD%(name)-s$RESET][%(levelname)-s] %(message)s %(lineno)d)"
    COLOR_FORMAT = formatter_message(FORMAT, True)
    to_console = True
    
    def __init__(self, name):
        # By default level is set to INFO
        logging.Logger.__init__(self, name, logging.INFO)
        logging.basicConfig(filename='/tmp/nfquery.log')
        color_formatter = ColoredFormatter(self.COLOR_FORMAT)
        if self.to_console: 
            # Console Logging 
            console = logging.StreamHandler()
            console.setFormatter(color_formatter)
            self.addHandler(console)

