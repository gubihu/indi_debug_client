# for logging
import sys
import time
import logging
# import the PyIndi module
import PyIndi

import numpy as np
import matplotlib.pyplot as plt


# Fancy printing of INDI states
# Note that all INDI constants are accessible from the module as PyIndi.CONSTANTNAME
def strISState(s):
    if s == PyIndi.ISS_OFF:
        return "Off"
    else:
        return "On"


def strIPState(s):

    if s == PyIndi.IPS_IDLE:
        return "Idle"
    elif s == PyIndi.IPS_OK:
        return "Ok"
    elif s == PyIndi.IPS_BUSY:
        return "Busy"
    elif s == PyIndi.IPS_ALERT:
        return "Alert"


# The IndiClient class which inherits from the module PyIndi.BaseClient class
# It should implement all the new* pure virtual functions.
class IndiClient(PyIndi.BaseClient):

    def __init__(self):
        super(IndiClient, self).__init__()
        self.logger = logging.getLogger('IndiClient')
        self.logger.info('creating an instance of IndiClient')
        self.t1 = []
        self.t2 = []
        self.y1 = []
        self.y2 = []
        self.axis1_t = []
        self.axis1_step = []
        self.axis1_deg = []
        self.axis1_init = None
        self.axis2_t = []
        self.axis2_step = []
        self.axis2_deg = []
        self.axis2_init = None
        self.speed_t = []
        self.speed_axis1 = []
        self.speed_axis2 = []
        self.fig, self.ax, self.l1, self.l2, self.l3, self.l4, self.l5, self.l6 = self.init_fig()
        self. start_time = time.time()

    def newDevice(self, d):
        self.logger.info("new device " + d.getDeviceName())

    def newProperty(self, p):
        self.logger.info("new property " + p.getName() + " for device "+ p.getDeviceName())

    def removeProperty(self, p):
        self.logger.info("remove property " + p.getName() + " for device "+ p.getDeviceName())

    def newBLOB(self, bp):
        self.logger.info("new BLOB " + bp.name.decode())

    def newSwitch(self, svp):
        self.logger.info ("new Switch " + svp.name + " for device "+ svp.device)

    def newNumber(self, nvp):
        self.logger.info("new Number " + nvp.name + F": {nvp.np.value}" + " for device " + nvp.device)

    def newText(self, tvp):
        self.logger.info("new Text " + tvp.name + " for device " + tvp.device)

    def newLight(self, lvp):
        self.logger.info("new Light " + lvp.name.decode() + " for device " + lvp.device.decode())

    def newMessage(self, d, m):
        pass
        self.logger.info("new Message " + d.messageQueue(m))

    def serverConnected(self):
        self.logger.info("Server connected ("+self.getHost()+":"+str(self.getPort())+")")

    def serverDisconnected(self, code):
        self.logger.info("Server disconnected (exit code = "+str(code)+","+str(self.getHost())+":"+str(self.getPort())+")")

    def init_fig(self):
        fig, ax = plt.subplots()
        l1, = ax.plot(self.t1, self.y1, '-')
        l1.set_label(F"AXIS1 (Az) err")
        l2, = ax.plot(self.t2, self.y2, '-')
        l2.set_label(F"AXIS2 (Alt) err")
        l3, = ax.plot(self.axis1_t, self.axis1_step, '-')
        l3.set_label(F"AXIS1 (Az) pos delta")
        l4, = ax.plot(self.axis2_t, self.axis2_step, '-')
        l4.set_label(F"AXIS2 (Alt) pos delta")
        l5, = ax.plot(self.speed_t, self.speed_axis1, '-')
        l5.set_label(F"AXIS1 (Az) speed")
        l6, = ax.plot(self.speed_t, self.speed_axis2, '-')
        l6.set_label(F"AXIS2 (Alt) speed")
        ax.set_xlabel("time [s]")
#        ax.set_xlim(self.x[0], self.x[-1])
        ax.set_ylabel("microstep")
#        ax.set_yticks(self.expticks)
        ax.set_ylim(-500, 500)
        ax.set_xlim(0, 1000)
        ax.grid()
        ax.legend()
        return fig, ax, l1, l2, l3, l4, l5, l6

    def show(self):
        if len(self.t1) > 0:
            xminmax = min(self.t1), max(self.t1)
            xlim = self.ax.get_xlim()
            xlen = xlim[1]-xlim[0]
            xmin = xminmax[1] - xlen
            xmax = xmin + xlen
            # if xminmax[1] > 2000:
            #     xmin = xminmax[1] - 2000
            # else:
            #     xmin = 0
            # xmax = xminmax[1] + 100
        else:
            xmin, xmax = self.ax.get_xlim()
        self.l1.set_xdata(self.t1)
        self.l1.set_ydata(self.y1)
        self.l2.set_xdata(self.t1)
        self.l2.set_ydata(self.y2)
        self.l3.set_xdata(self.axis1_t)
        self.l3.set_ydata(self.axis1_step)
        self.l4.set_xdata(self.axis2_t)
        self.l4.set_ydata(self.axis2_step)
        self.l5.set_xdata(self.speed_t)
        self.l5.set_ydata(self.speed_axis1)
        self.l6.set_xdata(self.speed_t)
        self.l6.set_ydata(self.speed_axis2)
        self.ax.set_xlim(xmin, xmax)
        self.fig.show()


class AxisOffsetClient(IndiClient):
    def newNumber(self, nvp):
        t = time.time() - self.start_time
        if nvp.name == "TRACKING_OFFSETS":
            az = nvp[0].value
            alt = nvp[1].value
            # print(F"Offsets: {t:.1f} Az: {az}, Alt: {alt}")
            self.t1.append(t)
            self.y1.append(az)
            self.y2.append(alt)
        if nvp.name == "AXIS1_ENCODER_VALUES":
            if self.axis1_init:
                self.axis1_t.append(t)
                self.axis1_step.append(nvp[2].value-self.axis1_init)
                self.axis1_deg.append(nvp[3].value)
                self.axis1_init = nvp[2].value
            else:
                self.axis1_init = nvp[2].value
#            print(F"AXIS1_ENCODER_VALUES: {nvp[2].value} step {nvp[3].value} deg")
        if nvp.name == "AXIS2_ENCODER_VALUES":
            if self.axis2_init:
                self.axis2_t.append(t)
                self.axis2_step.append(nvp[2].value-self.axis2_init)
                self.axis2_deg.append(nvp[3].value)
                self.axis2_init = nvp[2].value
            else:
                self.axis2_init = nvp[2].value
#            print(F"AXIS2_ENCODER_VALUES: {nvp[2].value} step {nvp[3].value} deg")
        if nvp.name == "TRACKING_SPEED":
            az = nvp[0].value
            alt = nvp[1].value
            # print(F"Offsets: {t:.1f} Az: {az}, Alt: {alt}")
            self.speed_t.append(t)
            self.speed_axis1.append(az)
            self.speed_axis2.append(alt)


logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        host = sys.argv[1]
    else:
        host = "localhost"
    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    else:
        port = 7624

    # Create an instance of the IndiClient class and initialize its host/port members
    self=AxisOffsetClient()
    self.setServer("localhost",7624)

    # Connect to server
    print("Connecting and waiting 1 sec")
    if not(self.connectServer()):
        print("No indiserver running on " + self.getHost() + ":" + str(self.getPort()))
        sys.exit(1)
    time.sleep(1)

    while True:
        self.show()
        plt.pause(1)

    # Disconnect from the indiserver
    # print("Disconnecting")
    # self.disconnectServer()
