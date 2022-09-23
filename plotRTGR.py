import time
import zmq
import threading
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import savemat
from scipy.signal import resample_poly
from matplotlib.animation import FuncAnimation

# Real-Time Stream 5 seconds worth of data before cycling it out
samp_rate = 500e3
window_size = 100
data_rate = samp_rate/window_size
plot_time = 15
avg_interval = 30 # Processing Interval (Seconds)
num_plot_samps = int(np.ceil(plot_time*data_rate))
num_est_samps = int(np.ceil(avg_interval*data_rate))
data_samps = np.zeros(num_est_samps)
plot_samps = np.zeros(num_plot_samps)
plot_range = np.arange(0,num_plot_samps)/data_rate
decim_rate = 10.0

# Setup ZMQ
context = zmq.Context()
consumer_receiver = context.socket(zmq.PULL)
consumer_receiver.connect("tcp://127.0.0.1:5557")
n_rx_samps = 0

def update(frame):
    line.set_ydata(plot_samps)
    ax.relim()
    ax.autoscale_view()
    return line,


def zmq_handler():
    global data_samps
    global plot_samps
    global n_rx_samps
    while True:
        buff = consumer_receiver.recv()
        data = np.frombuffer(buff, dtype="float32")
        n_rx_samps += data.size
        data_samps = np.concatenate((data_samps, data),axis=None)
        plot_samps = np.unwrap(data_samps[-num_plot_samps:])


def estimateVitals(frame):
    # DC Trend Removal
    est_samps = np.unwrap(data_samps[-num_est_samps:])
    x = np.arange(0,num_est_samps)/data_rate
    offset = np.polyfit(x, est_samps, 5)
    dcpoly = np.poly1d(offset)
    dcoffset = dcpoly(x)
    dcrem = est_samps - dcoffset
    dcrem_filt = resample_poly(dcrem,1,decim_rate)
    # FFT For RR
    freq = np.fft.rfft(dcrem_filt)
    f = np.fft.rfftfreq(int(num_est_samps/decim_rate), d = 1. /data_rate / decim_rate)
    rrmax = np.argmax(freq)
    print(f[rrmax])
    line2.set_ydata(dcrem_filt)
    ax2.relim()
    ax2.autoscale_view()
    line3.set_xdata(f)
    line3.set_ydata(10*np.log10(np.abs(freq)))
    ax3.relim()
    ax3.autoscale_view()
    return line2,


if __name__ == '__main__':
    thread = threading.Thread(target=zmq_handler)
    thread.daemon = True
    thread.start()

    fig = plt.figure()
    plt.subplot(311)
    line, = plt.plot(plot_range, plot_samps)
    plt.title("Real-Time Radar Phase Measurement")
    ax = plt.gca()
    animation = FuncAnimation(fig, update, interval=1000)
    plt.subplot(312)
    line2, = plt.plot(np.arange(0,num_est_samps/decim_rate)/data_rate, data_samps[-int(num_est_samps/decim_rate):])
    plt.title("DC Removed Respiratory Estimation Data")
    ax2 = plt.gca()
    anim2 = FuncAnimation(fig, estimateVitals, interval=15000)
    plt.subplot(313)
    line3, = plt.plot(np.arange(0,data_rate/decim_rate), data_samps[-int(data_rate/decim_rate):])
    ax3 = plt.gca()
    plt.title("Respiratory Rate Frequency Plot")
    plt.show()
