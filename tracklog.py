import numpy as np
import matplotlib.pyplot as plt


def get_limits(t1, t2, lim):
    if lim:
        return lim
    if len(t1) == 0:
        mint1 = 0
        maxt1 = 0
    else:
        mint1 = min(t1)
        maxt1 = max(t1)
    if len(t2) == 0:
        mint2 = 0
        maxt2 = 0
    else:
        mint2 = min(t2)
        maxt2 = max(t2)
    return min(mint1, mint2), max(maxt1, maxt2)


class Tracklog:

    def __init__(self, fname = None):
        self.t1 = []
        self.t2 = []
        self.y1 = []
        self.y2 = []
        self.fig, self.ax, self.l1, self.l2 = self.init_fig()
        self.enc1_last = 0
        self.enc1_t_last = 0
        self.enc2_last = 0
        self.enc2_t_last = 0
        self.enc1_t = []
        self.enc1_enc = []
        self.enc2_t = []
        self.enc2_enc = []
        self.fname = fname

    def init_fig(self):
        fig, ax = plt.subplots()
        l1, = ax.plot(self.t1, self.y1, '-')
        l1.set_label(F"AXIS1 (Az)")
        l2, = ax.plot(self.t2, self.y2, '-')
        l2.set_label(F"AXIS2 (Alt)")
        ax.set_xlabel("time [s]")
#        ax.set_xlim(self.x[0], self.x[-1])
        ax.set_ylabel("microstep")
#        ax.set_yticks(self.expticks)
        ax.set_ylim(-500, 500)
        ax.grid()
        ax.legend()
        return fig, ax, l1, l2

    def process_tracking_offset(self, axis, t, offset, rate):
        if axis == 1:
#            print(F"{t}: A1 {offset} {rate}")
            self.t1.append(t)
            self.y1.append(offset)
#            t_ser = np.append(self.l1.get_xdata(), t)
#            of_ser = np.append(self.l1.get_ydata(), offset)
        if axis == 2:
#            print(F"{t}: A2 {offset} {rate}")
            self.t2.append(t)
            self.y2.append(offset)
#            t_ser = np.append(self.l2.get_xdata(), t)
#            of_ser = np.append(self.l2.get_ydata(), offset)
#            self.l2.set_xdata(t_ser)
#            self.l2.set_ydata(of_ser)

    def process_axis_encoder(self, axis, t, encoder, intial, deg):
        if axis == 1:
#            print(F"{t}: AXIS1 Encoder {encoder} {deg}")
            if self.enc1_t_last > 0:
                self.enc1_t.append(t)
                self.enc1_enc.append((encoder - self.enc1_last)/(t-self.enc1_t_last))
#            if abs(self.enc1_last - encoder) > 1000:
            self.enc1_last = encoder
            self.enc1_t_last = t
        if axis == 2:
#            print(F"{t}: AXIS2 Encoder {encoder} {deg}")
            if self.enc2_t_last > 0:
                self.enc2_t.append(t)
                self.enc2_enc.append((encoder - self.enc2_last)/(t-self.enc2_t_last))
#            if abs(self.enc2_last - encoder) > 1000:
            self.enc2_last = encoder
            self.enc2_t_last = t
        pass

    def load_file(self, file):
        self.t1 = []
        self.t2 = []
        self.y1 = []
        self.y2 = []
        self.enc1_last = 0
        self.enc1_t_last = 0
        self.enc2_last = 0
        self.enc2_t_last = 0
        self.enc1_t = []
        self.enc1_enc = []
        self.enc2_t = []
        self.enc2_enc = []
        for line in file:
            words = line.split()
            t = float(words[1])
            if words[4] == "Tracking" and words[5] == "-" and words[7] == "offset":
                if words[6] == "AXIS1":
                    axis = 1
                elif words[6] == "AXIS2":
                    axis = 2
                else:
                    continue
                offset = int(words[8])
                rate = int(words[11]) * 2 * (int(words[13]) - 0.5)
                self.process_tracking_offset(axis, t, offset, rate)
            if words[4] == "Axis1" and words[5] == "encoder":
                encoder = int(words[6])
                initial = int(words[8])
                az = float(words[10])
                self.process_axis_encoder(1, t, encoder, initial, az)
            if words[4] == "Axis2" and words[5] == "encoder":
                encoder = int(words[6])
                initial = int(words[8])
                alt = float(words[10])
                self.process_axis_encoder(2, t, encoder, initial, alt)
        print(F"Offsets: {len(self.t1)}, {len(self.t2)}; Axis: {len(self.enc1_t)}, {len(self.enc2_t)}")

    def show(self, xlim=None, ylim=None):
        self.l1.set_xdata(self.t1)
        self.l1.set_ydata(self.y1)
        self.l2.set_xdata(self.t2)
        self.l2.set_ydata(self.y2)
        self.ax.set_xlim(get_limits(self.t1, self.t2, xlim))
        if ylim:
            self.ax.set_ylim(ylim)
#        self.ax.set_xbound(np.min([self.l1.get_xdata().min(), self.l2.get_xdata().min()]),
#                           np.max([self.l1.get_xdata().max(), self.l2.get_xdata().max()]))
        self.fig.show()

    def show_encoders(self, xlim=None, ylim=None):
        self.l1.set_xdata(self.enc1_t)
        self.l1.set_ydata(self.enc1_enc)
        self.l2.set_xdata(self.enc2_t)
        self.l2.set_ydata(self.enc2_enc)
        self.ax.set_xlim(get_limits(self.enc1_t, self.enc2_t, xlim))
        if ylim:
            self.ax.set_ylim(ylim)
        self.fig.show()

    def show_interactive(self):
        while True:
            with open(self.fname) as f:
                self.load_file(f)
            xlim = get_limits(self.t1, self.t2, None)
            if xlim[1] > 2000:
                xmin = xlim[1] - 2000
            else:
                xmin = 0
            self.show((xmin, xlim[1]+100))
            plt.pause(1)


def_fname = "indi_skywatcherAltAzMount_0213_1.log"

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        fname = sys.argv[1]
    else:
        fname = def_fname
    self = Tracklog(fname)
    with open(self.fname) as f:
        self.load_file(f)
    self.show_interactive()
