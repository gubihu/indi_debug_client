import socket

localIP = "127.0.0.1"
AllIP = "0.0.0.0"
myIP = "192.168.88.64"

localPort = 11880

bufferSize = 1024

msgFromServer = "Hello UDP Client"

bytesToSend = str.encode("=\r")

VERSION_STRING = "0210A1"
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

print("UDP server up and listening")

# Listen for incoming datagrams

position = [0, 0, ]


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
    return i.to_bytes(l, 'little').hex()


def inquire_version(axis, data):
    return "=", VERSION_STRING


def inquire_status(axis, data):
    return "=", IDLE_STATUS_STRING


def inquire_microsteps_per_rev(axis, data):
    return "=", MICROSTEPS_PER_REV_STRING


def inquire_stepper_freq(axis, data):
    return "=", STEPPER_FREQUENCY_STRING


def inquire_highspeed_ratio(axis, data):
    return "=", HIGHSPEED_RATIO_STRING


def inquire_position(axis, data):
    position[axis] = position[axis] + 100000
    print(F"Inquire Position {axis+1}: {position[axis]}")
    return "=", int2hexb(position[axis], 3).encode()


def set_position(axis, data):
    position[axis] = hex2int(data)
    return "=", ""


while True:
    message_raw, address = UDPServerSocket.recvfrom(bufferSize)
    message = message_raw.decode()
#    message = bytesAddressPair[0]

#    address = bytesAddressPair[1]

    # echo
    UDPServerSocket.sendto(message_raw, address)

    clientMsg = F"Message from Client:{message}"
    clientIP = F"Client IP Address:{address}"

    print(clientMsg)
    print(clientIP)

    # Sending a reply to client

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
                    print('Inquire Version')
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
                    print(F"Inquire Status {axis}")
                    ok, resp = inquire_status(axis, data)
                if command == 'j':
                    ok, resp = inquire_position(axis, data)
                if command == "E":
                    print(F"Set position {axis} {data}")
                    ok, resp = set_position(axis, data)
                if not resp:
                    resp = "0"  # unknown command
                    print(F"Unknown command: {command}")
            else:
                resp = "3"  # unknown character
        if not resp is None:
            bytesToSend = F"{ok}{resp}\r".encode()
            UDPServerSocket.sendto(bytesToSend, address)
    else:
        print("Message malformed")