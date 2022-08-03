import struct

from rsl_comm_py import UM7Serial
from time import time
import logging



um7_serial = UM7Serial(port_name='/dev/serial0')

start = 0xAD
length = 0
data = None
no_read = False

hidden = start & 0xf000
sa = start & 0xff
pt = 0x0
if data:
    pt = 0b11000000
    pt |= (length << 2)
if hidden:
    pt |= 0b00000010
ba = bytearray([ord('s'), ord('n'), ord('p'), pt, sa])
if data:
    ba += data
cs = sum(ba)
ba += struct.pack('!h', cs)
um7_serial.send(ba)
ok, _ = um7_serial.find_response(0xad)

path = '/home/kngik/Desktop/PW_underwater/data/imu/' + str(time()).replace('.', '_') + '.txt'

with open(path, 'w') as f:
    for packet in um7_serial.recv_euler_broadcast():
        print(f"packet: {packet}")
        f.write(str(packet) + '\n')
