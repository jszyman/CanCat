#!/usr/bin/env python
import time
import cancat
import struct
import threading

class UDS:
    def __init__(self, c, tx_arbid, rx_arbid):
        self.c = c
        self.tx_arbid = tx_arbid
        self.rx_arbid = rx_arbid

    def SendTesterPresent(self):
        while self.TesterPresent is True:
            self.c.CANxmit(self.tx_arbid, "023E000000000000".decode('hex'))
            time.sleep(2.0)

    def StartTesterPresent(self):
        self.TesterPresent = True
        self.t = threading.Thread(target = self.SendTesterPresent)
        self.t.setDaemon(True)
        self.t.start()

    def StopTesterPresent(self):
        self.TesterPresent = False
        self.t.join(5.0)
        if self.t.isAlive():
            print "Error killing Tester Present thread"
        else:
            del self.t

    def DiagnosticSessionControl(self, session):
        arbid, msg = self.c.ISOTPxmit_recv(self.tx_arbid, self.rx_arbid, "\x10" + chr(session), service=0x50)
        print arbid, msg.encode('hex')
        
    def SecurityService(self, level):
        arbid, msg = self.c.ISOTPxmit_recv(self.tx_arbid, self.rx_arbid, "\x27" + chr(level))
        print arbid, msg.encode('hex')
        if(msg[1] == 0x7f):
            print "Error getting seed:", msg
        else:
            seed = msg[3:6]

            key = seed # Replace this with a call to the actual response computation function
            currIdx = self.c.getCanMsgCount()
            self.c.ISOTPxmit_recv(self.tx_arbid, self.rx_arbid, "\x27" + chr(level+1) + key)
            arbid, msg = self.ReassembleIsoTP(start_index = currIdx, service = 0x67)
            print arbid, msg.encode('hex')

    def readDID(self, ecuarbid, did, resparbid=None):
        if resparbid == None:
            resparbid = ecuarbid + 8 # by ISO-TP Spec

        arbid, msg = self.c.ISOTPxmit_recv(ecuarbid, resparbid, "22".decode('hex') + struct.pack('>H', did), service=0x67)
        
        return arbid, msg

