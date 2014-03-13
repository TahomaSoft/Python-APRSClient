from APRSClient import APRSParser
from termcolor import colored

packet=[]
packet.append("VE6BRF-9>APTT4,WIDE1-1,WIDE2-1,qAR,VE6EAW:T#513,176,255,255,099,255,00000000")
packet.append("VE6BRF-9>APTT4,WIDE1-1,WIDE2-1,qAR,VE6EAW:@000000h5140.77N/11444.79WK000/000/TinyTrak4 17.9V herb@beer.org/A=004331")
packet.append("VE6BRF-9>APTT4,CARSTR,WIDE1*,WIDE2-1,qAR,VE6EAW:T#503,177,255,255,100,255,00000000")

while len(packet):
	this_packet = packet.pop()
        aprs=APRSParser(this_packet)
        print "-----------------------------------------------------------------------------------------------------------"
        print "RAW PACKET : " + this_packet
	parsed = aprs.parse()
        print "CALLSIGN   : " + colored(parsed["callsign"], 'yellow')
        print "DESTINATION: " + colored(parsed["destination"], 'cyan')
        print "PATH       : " + parsed["path"]
        print "DATA       : " + parsed["data"]
        print "  TYPE     : " + aprs.data_type_verbose(aprs.get_data_type(parsed["data"]))
	if aprs.get_data_type(parsed["data"]) == 'T':
            print aprs.parse_telemetry(parsed["data"])
