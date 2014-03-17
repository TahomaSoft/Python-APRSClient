#!/usr/bin/env python

# Import required modules
from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import LineReceiver
from twisted.internet.serialport import SerialPort
from twisted.internet import reactor
from termcolor import colored
import sys, re
from APRSParser import APRSParser

# Variables that we'll need later
server = None
port = None
callsign = None
passcode = None
receive_filter = None

# The actual APRS-IS connector
class APRSISConnector(LineReceiver):

    def connectionMade(self):
        print colored(server + " <<< " + "Logging in...", 'cyan')
        self.sendLine("user " + callsign + " pass " + passcode + " vers Python/APRS 0.1 filter " + receive_filter)

    def lineReceived(self, line):
        print line
        parser = APRSParser(line)
        print parser.parse()

# APRSISConnector factory class
class APRSISConnectorFactory(ClientFactory):
    protocol = APRSISConnector

    def clientConnectionFailed(self, connector, reason):
        print 'connection failed:', reason.getErrorMessage()
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        print 'connection lost:', reason.getErrorMessage()
        reactor.stop()

class APRSSerial(LineReceiver):

    def processData(self, data):
        print "processData:"+data

    def connectionMade(self):
        print 'Connected to TNC'

    def lineReceived(self, data):
        print "Received: {0}".format(data)
        parser=APRSParser(data)
        #
        # After this, we'll have a callsign, destination, path, and 'data'.
	parsed = parser.parse()
        return parsed

class APRSClientException(Exception):
    def __init__(self, value):
      self.value = value
    def __str__(self):
      return repr(self.value)

def APRSISConnect(server_arg, port_arg, handler):
    global server, port
    server = server_arg
    port = port_arg
    print "Connecting to APRS server " + server + ", port " + str(port)
    try:
      if callsign is None or passcode is None or receive_filter is None:
        raise APRSClientException("Missing callsign, passcode or filter.")
      factory = APRSISConnectorFactory()
      reactor.connectTCP(server, port, factory)
      reactor.run()
    except APRSClientException, e:
      print e.value

def APRSSerialConnect(port, baudrate):
    s = SerialPort(APRSSerial(), port, reactor, baudrate=baudrate)
    reactor.run()

if __name__ == '__main__':
    main()
