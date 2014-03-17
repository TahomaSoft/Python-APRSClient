# APRSParser class

import sys, re

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
        print self.packet
      else:
        # Assume we have an APRS message, so...
        # Pull the source callsign, destination, path and data from the raw packet
        packet_segments = re.search('([\w\-]+)>([\w\-]+),([\w\-\*\,]+):(.*)', self.packet)
        if packet_segments is not None:
          (parsed["callsign"], parsed["destination"], parsed["path"], parsed["data"]) = packet_segments.groups()
        else:
          # We couldn't parse the packet
          print "Could not parse - possibly non-packet data from server?"
      return parsed

  # Validate data_type.
  def get_data_type(self, data):
    type = data[0]
    if self.data_types.get(type) is None:
        return None
    else:
        return type

  # Convert data_type to a string.
  def data_type_verbose(self, data_type):
    return self.data_types.get(self.get_data_type(data_type))

  def parse_telemetry(self, data):
    telem={}
    r = re.search('^T#([0-9].*),([0-9].*),([0-9].*),([0-9].*),([0-9].*),([0-9].*),([01].*)$', data)
    if r is not None:
        (telem["sequence"], telem["ch1"], telem["ch2"], telem["ch3"], telem["ch4"],telem["ch5"],telem["bits"]) = r.groups()
    return telem

  def parse_message(self, data):
    return data[1:].strip()

  def parse_id(self, data):
    data_type = self.get_data_type(data)
    # Check we have a valid data type
    if data_type is None:
      # The spec allows '!' (and *only* '!') to appear anywhere in the first 40 characters of the data string to be valid
      # (To support Fixed format digipeaters (no APRS), what do we do with this?)
      if '!' in data[0:40]:
        return self.get_data_type(data_type) + " ('!' at position " + str(check_for_bang.start()) + ")"
      else:
        # Couldn't find '!' in the first 40 characters either, so return 'Unknown'
        return "Unknown"
    else:
      # Return the data type
      return data_type

