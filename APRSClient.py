#!/usr/bin/env python

# Import required modules
from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor
from termcolor import colored
import sys, re

# Variables that we'll need later
server = None
port = None
callsign = None
passcode = None
receive_filter = None

# The actual APRS-IS connector
class APRSConnector(LineReceiver):

    def connectionMade(self):
        print colored(server + " <<< " + "Logging in...", 'cyan')
        self.sendLine("user " + callsign + " pass " + passcode + " vers Python/APRS 0.1 filter " + receive_filter)

    def lineReceived(self, line):
        parser = APRSParser(line)
        parser.parse()

# APRSConnector factory class
class APRSConnectorFactory(ClientFactory):
    protocol = APRSConnector

    def clientConnectionFailed(self, connector, reason):
        print 'connection failed:', reason.getErrorMessage()
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        print 'connection lost:', reason.getErrorMessage()
        reactor.stop()

# APRSParser class
class APRSParser:
  packet = None

  # These data types are taken directly from the APRS spec at http://aprs.org/doc/APRS101.PDF
  # This is not an exhaustive list. These are the most common ones, and were added during
  # testing.
  data_types = {'!' : 'Position without timestamp',
                    '_' : 'Weather Report (without position)',
                    '@' : 'Position with timestamp (with APRS messaging)',
                    '/' : 'Position with timestamp (no APRS messaging)',
                    '=' : 'Position without timestamp (with APRS messaging)',
                    'T' : 'Telemetry data',
                    ';' : 'Object',
                    '<' : 'Station Capabilities',
                    '>' : 'Status',
                    '`' : 'Current Mic-E Data (not used in TM-D700)',
                    '?' : 'Query',
                    '\'' : 'Old Mic-E Data (but Current data for TM-D700)',
                    ':' : 'Message',
                    '$' : 'Raw GPS data or Ultimeter 2000',
                    }

  def __init__(self, packet):
    self.packet = packet

  def parse(self):
    parsed={}
    if self.packet is not None:
      if self.packet[0] == "#":
        # We have a message beginning with '#' (a server message)
        global server
        print colored(server + " >>> " + self.packet, 'green')
      else:
        # Assume we have an APRS message, so...
        # Pull the source callsign, destination, path and data from the raw packet
        packet_segments = re.search('([\w\-]+)>([\w\-]+),([\w\-\*\,]+):(.*)', self.packet)
        if packet_segments is not None:
          (parsed["callsign"], parsed["destination"], parsed["path"], parsed["data"]) = packet_segments.groups()
  
        else:
          # We couldn't parse the packet
          print colored("Could not parse - possibly non-packet data from server?", 'red')
        return parsed

##  def parse_telemetry(self, data):
##    telem={}

  def parse_id(self, data):
    # Get the first character of the data field, and look it up
    type_id = data[0]
    data_type = self.data_types.get(type_id)
    # Check we have a valid data type
    if data_type is None:
      # The spec allows '!' (and *only* '!') to appear anywhere in the first 40 characters of the data string to be valid
      check_for_bang = re.search('!', data[0:40])
      if check_for_bang is not None:
        return colored(self.data_types.get('!'), 'green') + " ('!' at position " + str(check_for_bang.start()) + ")"
      else:
        # Couldn't find '!' in the first 40 characters either, so return 'Unknown'
        return colored("Unknown", 'magenta')
    else:
      # Return the data type
      return colored(data_type, 'green')

class APRSClientException(Exception):
    def __init__(self, value):
      self.value = value
    def __str__(self):
      return repr(self.value)

def connect(server_arg, port_arg):
    global server, port
    server = server_arg
    port = port_arg
    print "Connecting to APRS server " + server + ", port " + str(port)
    try:
      if callsign is None or passcode is None or receive_filter is None:
        raise APRSClientException("Missing callsign, passcode or filter.")
      factory = APRSConnectorFactory()
      reactor.connectTCP(server, port, factory)
      reactor.run()
    except APRSClientException, e:
      print e.value

if __name__ == '__main__':
    main()
