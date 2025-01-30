"""
A skeleton from which you should write your client.
"""

import socket
import json
import argparse
import logging
import select
import sys
import time
import datetime
import struct
from socket import timeout

from message import UnencryptedIMMessage

def parseArgs():
    """
    parse the command-line arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', '-p', 
        dest="port", 
        type=int, 
        default='9999',
        help='port number to connect to')
    parser.add_argument('--server', '-s', 
        dest="server", 
        required=True,
        help='server to connect to')       
    parser.add_argument('--nickname', '-n', 
        dest="nickname", 
        required=True,
        help='nickname')                
    parser.add_argument('--loglevel', '-l', 
        dest="loglevel",
        choices=['DEBUG','INFO','WARN','ERROR', 'CRITICAL'], 
        default='INFO',
        help='log level')
    args = parser.parse_args()
    return args


def main():
    args = parseArgs()

    # set up the logger
    log = logging.getLogger("myLogger")
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s')
    level = logging.getLevelName(args.loglevel)
    
    log.setLevel(level)
    log.info(f"running with {args}")
    
    log.debug(f"connecting to server {args.server}")
    try:
        s = socket.create_connection((args.server,args.port))
        log.info("connected to server")
    except:
        log.error("cannot connect")
        exit(1)

    # here's a nice hint for you...
    readSet = [s] + [sys.stdin]

    while True:
        potentialReaders = [readSet]
        potentialWriters = []
        potentialErrs = []
        readyToRead = []
        readyToWrite = []
        inErr = []
        readyToRead, readyToWrite, inErr = select.select(
            potentialReaders,
            potentialWriters,
            potentialErrs,
            timeout)
        for source in readyToRead:
            #Case1: reads from standard input and sends whatever was typed by the user to the BasicIM server;
            if source is sys.stdin:
                userMessage = sys.stdin.readline()
                if userMessage:
                    msg = UnencryptedIMMessage(args.nickname, userMessage)
                    (packedSize,jsonData) = msg.serialize()
                    s.send(struct.unpack("!L",packedSize)[0])
                    s.send(jsonData)
            #Case2: reads from a network socket (connected to the BasicIM server) and receives messages (via the server), 
            # which it then displays to standard output (i.e., it prints out the received messages).
            if source is s:
                packedLen = s.recv(4, socket.MSG_WAITALL)
                unpackedSize = struct.unpack("!L", packedLen)[0]
                messageBody = s.recv(unpackedSize, socket.MSG_WAITALL)
                msg = UnencryptedIMMessage.parseJSON(messageBody)
                print(msg)

        
        # # DELETE THE NEXT TWO LINES. It's here now to prevent busy-waiting.
        # time.sleep(1)
        # log.info("not much happening here.  someone should rewrite this part of the code.")

        

if __name__ == "__main__":
    exit(main())

