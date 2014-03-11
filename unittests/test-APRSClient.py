import APRSClient

server="rotate.aprs2.net"
port=14580

aprs=APRSClient
aprs.callsign = 'VE6BRF'
aprs.passcode = '55512'
aprs.receive_filter = 'b/VE6BRF-9'

aprs.connect (server, port)
