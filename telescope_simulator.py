import time
import socket

localIP = "127.0.0.1"
AllIP = "0.0.0.0"
myIP = "192.168.88.64"

localPort = 11880

bufferSize = 1024

msgFromServer = "Hello UDP Client"

bytesToSend = str.encode("=\r")

VERSION_STRING = "0210A1"
INIT_STATUS_STRING = "001"
IDLE_STATUS_STRING = "101"
MICROSTEPS_PER_REV_STRING = "1A330D"
STEPPER_FREQUENCY_STRING = "204E00"
HIGHSPEED_RATIO_STRING = "20"

MICROSTEPS_PER_REV = 865050
STEPPER_FREQUENCY = 20000
HIGHSPEED_RATIO = 32

# Create a datagram socket

UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and ip

UDPServerSocket.bind((AllIP, localPort))

UDPServerSocket.setblocking(0)

print("UDP server up and listening")

# Listen for incoming datagrams

position = [0x800000, 0x800000, ]
step_period = [0, 0, ]
running = [False, False, ]
motion_goto = [False, False, ]
motion_fast = [False, False, ]
motion_CW = [True, True, ]

def hex2int(s):
    if len(s) % 2 != 0:
        raise ValueError("Invalid length of hex string")
    res = 0
    for i in range(len(s), 0, -2):
        a = int(s[i-2:i], 16)
        res = 256*res + a
#    print(F"0x{res:x}")
    return res


def int2hexb(i, l=3):
    return i.to_bytes(l, 'little').hex().upper()


def inquire_version(axis, data):
    return "=", VERSION_STRING


def inquire_status(axis, data):
    return "=", IDLE_STATUS_STRING


def inquire_microsteps_per_rev(axis, data):
    return "=", int2hexb(MICROSTEPS_PER_REV, 3)


def inquire_stepper_freq(axis, data):
    return "=", int2hexb(STEPPER_FREQUENCY, 3)


def inquire_highspeed_ratio(axis, data):
    return "=", int2hexb(HIGHSPEED_RATIO, 1)


def inquire_position(axis, data):
    position[axis] = position[axis] # + 100000
    print(F"Inquire Position {axis+1}: {position[axis] - 0x800000}")
    return "=", int2hexb(position[axis], 3) #  + 0x800000


def set_position(axis, data):
    position[axis] = hex2int(data)
    print(F"Set position {axis+1} {position[axis] - 0x800000}")
    return "=", ""


def set_motion_mode(axis, data):
    mode = int(data[0])
    motion_goto[axis] = (mode & 0x01) == 0
    motion_fast[axis] = (mode & 0x02)>>1 == (mode & 0x01)
    motion_CW[axis] = (data[1] == '0')
    print(F"Set motion mode {axis+1}: {mode} GOTO: {motion_goto[axis]} FAST: {motion_fast[axis]} CW: {motion_CW[axis]}")
    return "=", ""


def set_step_period(axis, data):
    step_period[axis] = hex2int(data)
    print(F"Set step_period {axis+1} {step_period[axis]}")
    return "=", ""


def start_motion(axis, data):
#    step_period[axis] = hex2int(data)
    print(F"Start motion {axis+1} at stepper period {step_period[axis]}")
    running[axis] = True
    return "=", ""


def stop_motion(axis, data):
#    step_period[axis] = hex2int(data)
    print(F"Stop motion {axis+1}, was running: {running[axis]}")
    running[axis] = False
    return "=", ""


def process_message(messaage):
        if len(message) > 0 and message[0] == ':' and message[-1] == '\r':
            resp = None
            ok = "!"
            if len(message) > 2:
                command = message[1]
                axis = message[2]
                data = message[3:-1]
                if axis == "1" or axis == "2":
                    axis = int(axis) - 1
                    if command == 'e':
#                        print('Inquire Version')
                        ok, resp = inquire_version(axis, data)
                    if command == 'a':
                        print(F"Inquire Microsteps per revolution {axis}")
                        ok, resp = inquire_microsteps_per_rev(axis, data)
                    if command == 'b':
                        print(F"Inquire Stepper frequinecy {axis}")
                        ok, resp = inquire_stepper_freq(axis, data)
                    if command == 'g':
                        print(F"Inquire Highspeed ratio {axis}")
                        ok, resp = inquire_highspeed_ratio(axis, data)
                    if command == 'f':
#                        print(F"Inquire Status {axis}")
                        ok, resp = inquire_status(axis, data)
                    if command == 'j':
                        ok, resp = inquire_position(axis, data)
                    if command == "E":
                        ok, resp = set_position(axis, data)
                    if command == "G":
                        ok, resp = set_motion_mode(axis, data)
                    if command == "I":
                        ok, resp = set_step_period(axis, data)
                    if command == "J":
                        ok, resp = start_motion(axis, data)
                    if command == "K":
                        ok, resp = stop_motion(axis, data)
                    if resp is None:
                        resp = "0"  # unknown command
                        print(F"Unknown command: {command}")
                else:
                    resp = "3"  # unknown character
            if not resp is None:
    #            print(F"{ok}{resp}")
                bytesToSend = F"{ok}{resp}\r".encode()
                UDPServerSocket.sendto(bytesToSend, address)
        else:
            print("Message malformed")


if __name__ == "__main__":
    last = time.time()
    while True:
        try:
            message_raw, address = UDPServerSocket.recvfrom(bufferSize)  # , socket.MSG_DONTWAIT)
            message = message_raw.decode()
        #    message = bytesAddressPair[0]

        #    address = bytesAddressPair[1]

            # echo
            UDPServerSocket.sendto(message_raw, address)

            clientMsg = F"Message from Client {address}:{message}"

        #    print(clientMsg)

            # Sending a reply to client
            process_message(message)

        except BlockingIOError:
            pass
        now = time.time()
        ticks = (now - last) * STEPPER_FREQUENCY

        for axis in (0, 1):
            if running[axis]:
                if motion_goto[axis]:
                    if motion_fast[axis]:
                        step = 4
                    else:
                        step = 128
                else:
                    if motion_fast[axis]:
                        step = step_period[axis] / HIGHSPEED_RATIO
                    else:
                        step = step_period[axis]
                if motion_CW[axis]:
                    position[axis] = int(position[axis] + ticks / step) & 0xFFFFFF
                else:
                    position[axis] = int(position[axis] - ticks / step) & 0xFFFFFF
        last = now
        time.sleep(1/STEPPER_FREQUENCY)