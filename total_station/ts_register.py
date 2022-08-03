import os
import serial
import time
import datetime

# import config as cfg


GENERIC_OK = b'%R1P,0,0:0' + chr(13).encode() + chr(10).encode()
LOCK_OK = b'%R1P,0,0:0,1' + chr(13).encode() + chr(10).encode()


def send_command(handle, command):
    buf = chr(10).encode() + command + chr(13).encode() + chr(10).encode()
    # buf = b'\n' + command + b'\r' + b'\n'
    bytes_sent = leica.write(buf)
    leica.flush()
    return bytes_sent


def wait_for_response(handle):
    while True:
        time.sleep(0.01)
        rec = leica.readline()
        if rec != '':
            return rec


def execute_command(handle, command):
    send_command(handle, command)
    return wait_for_response(handle)


try:

    file_name = str(time.time()) + '.txt'
    file_save = open(file_name, 'w')
    line = 'response_code,x,y,z,timestamp\n'
    file_save.write(line)

    leica = serial.Serial('/dev/rfcomm0', 9600, timeout=5)

    if not leica.is_open:
        print('opening port')
        leica.open()

    ret = execute_command(leica, b'%R1Q,18007:1') # Set of the ATR lock switch


    while True:
        ret = execute_command(leica, b'%R1Q,9037:0.1,0.1,0') # Automatic target positioning : search_range_Hz, search_range_Hz, always False
        if ret == GENERIC_OK:
            print('target acquired')
            # lock in
            ret2 = execute_command(leica, b'%R1Q,9013:') # Starts the target tracking
            if ret2 == GENERIC_OK:
                print('target locked')
                # measure
                lock = True
                while lock:
                    # fast measure angles dist
                    # ret3 = execute_command(leica, b'%R1Q,2117:')

                    # dist then coord quite fast
                    ret3 = execute_command(leica, b'%R1Q,2008:1,1') # Carries out a distance measurement
                    ret3 = execute_command(leica, b'%R1Q,2116:1000,1') # Get cartesian coordinates
                    # ret3 = execute_command(leica, b'%R1Q,2082:1000,1')

                    # measure coords slow
                    # et3 = execute_command(leica, b'%R1Q,2117:')
                    # ret3 = execute_command(leica, b'%R1Q,2116:1000,1')

                    line = str(ret3[9:-2]) + ',' + str("%f" % time.time()) + '\n'
                    file_save.write(line)
                    print(line, end='')
                    ret4 = execute_command(leica, b'%R1Q,6021:') # Return condition of LockIn control
                    if ret4 != LOCK_OK:
                        lock = False
                        print('lock lost')

            time.sleep(2)
        else:
            print('target not acquired')
        print('BEEEEEEEEEEEEEEEEEEEEEEEEEEEP')
        ret = execute_command(leica, b'%R1Q,11004:') # triple beep
        time.sleep(3)
        ret = execute_command(leica, b'%R1Q,11003:') # single beep
        time.sleep(2)
        ret = execute_command(leica, b'%R1Q,11003:') # single beep
        time.sleep(2)
        ret = execute_command(leica, b'%R1Q,11003:') # single beep
        time.sleep(2)
        ret = execute_command(leica, b'%R1Q,11004:') # triple beep

    print("Done.\nExiting.")
except (KeyboardInterrupt, SystemExit):  # when you press ctrl+c
    ret = execute_command(leica, b'%R1Q,18007:0') #zwalnia lock
    print(ret)
    print("Done.\nExiting.")

    leica.close()
    print('Port closed!')
