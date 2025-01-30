import socket
import json
import argparse
import logging
import select
import struct
import time
from socket import timeout



def parseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', '-p', 
        dest="port", 
        type=int, 
        default='9999',
        help='port number to listen on')
    parser.add_argument('--loglevel', '-l', 
        dest="loglevel",
        choices=['DEBUG','INFO','WARN','ERROR', 'CRITICAL'], 
        default='INFO',
        help='log level')
    args = parser.parse_args()
    return args


def main():
    args = parseArgs()      # parse the command-line arguments

    # set up logging
    log = logging.getLogger("myLogger")
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s')
    level = logging.getLevelName(args.loglevel)
    log.setLevel(level)
    log.info(f"running with {args}")
    
    log.debug("waiting for new clients...")
    serverSock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    serverSock.bind(("",args.port))
    serverSock.listen()

    clientList = []

    potentialReaders = [serverSock]

    while True:
        
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
        
        for s in readyToRead:
            # it waits/listens for new connections from clients.  Note that the server should support clients joining or leaving at any time.
            if s is serverSock:
                (clientsocket, address) = serverSock.accept()
                clientList.append(clientsocket)
                potentialReaders.append(clientsocket)
                print("Client " + str(address) + " joined!")
            
            # upon receiving a message from a BasicIM client, it sends a copy of that message to every other currently connected client.  
            # The originator of the message should not get a copy.  (For example, if Alice is talking to Bob and Charlie, and Alice sends a message, 
            # the server should forward that received message to Bob and Charlie but not Alice.)
            else:
                packedLen = s.recv(4, socket.MSG_WAITALL)
                unpackedSize = struct.unpack("!L", packedLen)[0]
                messageBody = s.recv(unpackedSize, socket.MSG_WAITALL)
                for client in clientList:
                    if client is not s:
                        client.send(packedLen)
                        client.send(messageBody)
           

        # DELETE THE NEXT TWO LINES. It's here now to prevent busy-waiting.
        # time.sleep(1)
        # log.info("not much happening here.  someone should rewrite this part of the code.")

                            
    

if __name__ == "__main__":
    exit(main())

