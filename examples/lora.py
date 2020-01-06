##!/usr/bin/env python3
import io
import sys
import time
import datetime
import argparse
from enum import IntEnum
import serial
from serial.threaded import LineReader, ReaderThread

#python lorawan.py port /dev/ttyUSB0 --j abp --appskey 147755488987237987A9867DE942B113 --nwkskey BA0CDCB2D113BEF6B6F523E34668E26D --devaddr 26021918

parser = argparse.ArgumentParser(description='Connect to LoRaWAN network')
parser.add_argument('port', help="Serial port of LoStik")
parser.add_argument('--joinmode', '-j', help="otaa, abp", default="otaa")

# ABP credentials
parser.add_argument('--appskey', help="App Session Key", default="")
parser.add_argument('--nwkskey', help="Network Session Key", default="")
parser.add_argument('--devaddr', help="Device Address", default="")
parser.add_argument('--dr', help="Data Rate", default="3")
parser.add_argument('--adr', help="Adaptive Data Rate", default="off")
parser.add_argument('--sf', help="Spreading Factor", default="sf7")
parser.add_argument('--freq', help="Frequency", default="903900000")
parser.add_argument('--rx2', help="rxFreq&dataRate",default="8 923300000")
parser.add_argument('--delay',help="transmission delay",default="60000")

# OTAA credentials
parser.add_argument('--appeui', help="App EUI", default="")
parser.add_argument('--appkey', help="App Key", default="")
parser.add_argument('--deveui', help="Device EUI", default="")

args = parser.parse_args()

OTAA_RETRIES = 5

class MaxRetriesError(Exception):
    pass

class ConnectionState(IntEnum):
    SUCCESS = 0
    CONNECTING = 100
    CONNECTED = 200
    FAILED = 500
    TO_MANY_RETRIES = 520


class PrintLines(LineReader):

    retries = 0
    state = ConnectionState.CONNECTING

    def retry(self, action):
        if(self.retries >= OTAA_RETRIES):
            print("Too many retries, exiting")
            self.state = ConnectionState.TO_MANY_RETRIES
            return
        self.retries = self.retries + 1
        action()

    def get_var(self, cmd):
        self.send_cmd(cmd)
        return self.transport.serial.readline()

    def join(self):
        if args.joinmode == "abp":
            self.join_abp()
        else:
            self.join_otaa()

    def join_otaa(self):
        if len(args.appeui):
            self.send_cmd('mac set appeui %s' % args.appeui)
        if len(args.appkey):
            self.send_cmd('mac set appkey %s' % args.appkey)
        if len(args.deveui):
            self.send_cmd('mac set deveui %s' % args.deveui)
        self.send_cmd('mac join otaa')

    def join_abp(self):
        
        if len(args.devaddr):
            self.send_cmd('mac set devaddr %s' % args.devaddr)
        if len(args.appskey):
            self.send_cmd('mac set appskey %s' % args.appskey)
        if len(args.nwkskey):
            self.send_cmd('mac set nwkskey %s' % args.nwkskey)
        if len(args.dr):
            self.send_cmd('mac set dr %s' % args.dr)
        if len(args.adr):
            self.send_cmd('mac set adr %s' % args.adr)
        if len(args.sf):
            self.send_cmd('radio set sf %s' % args.sf)
        if len(args.freq):
            for i in range(72):
                if i!=8:
                    self.send_cmd('mac set ch status %s off'  % i)
                else:
                    self.send_cmd('mac set ch status %s on' % i)
        
     #   if len(args.rx2):
     #       self.send_cmd('mac set rx2 %s' % args.rx2)
      #  if len(args.delay):
      #      self.send_cmd('mac set rxdelay1 %s' %args.delay)
       
        self.send_cmd('mac join abp')
        self.send_cmd('mac save')
        
    def connection_made(self, transport):
        """
        Fires when connection is made to serial port device
        """
        print("Connection to LoStik established")
        self.transport = transport
        self.retry(self.join)

    def handle_line(self, data):
        # if data == "ok" or data == 'busy':
        #     return
        print("STATUS: %s" % data)
        if data.strip() == "denied" or data.strip() == "no_free_ch":
            print("Retrying OTAA connection")
            self.retry(self.join)
        elif data.strip() == "accepted":
            print("UPDATING STATE to connected")
            self.state = ConnectionState.CONNECTED

    def connection_lost(self, exc):
        """
        Called when serial connection is severed to device
        """
        if exc:
            print(exc)
        print("Lost connection to serial device")

    def send_cmd(self, cmd, delay=.5):
        print(cmd)
        self.transport.write(('%s\r\n' % cmd).encode('UTF-8'))
        time.sleep(delay)


ser = serial.Serial(args.port, baudrate=57600)
with ReaderThread(ser, PrintLines) as protocol:
    while protocol.state < ConnectionState.FAILED:
        if protocol.state != ConnectionState.CONNECTED:
            time.sleep(1)
            continue
        protocol.send_cmd("mac tx cnf 1 5A")# % int(time.time()))
        time.sleep(70)
    exit(protocol.state)

