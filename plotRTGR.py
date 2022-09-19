import time
import zmq
import threading
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Real-Time Stream 5 seconds worth of data before cycling it out
samp_rate = 500e3
window_size = 100
data_rate = samp_rate/window_size
plot_time = 10
avg_interval = 15 # Processing Interval (Seconds)
num_plot_samps = int(np.ceil(5*data_rate))
num_est_samps = int(np.ceil(avg_interval*data_rate))
data_samps = np.zeros(num_est_samps)
plot_samps = np.zeros(num_plot_samps)
plot_range = np.arange(0,num_plot_samps)/data_rate

# Setup ZMQ
context = zmq.Context()
consumer_receiver = context.socket(zmq.PULL)
consumer_receiver.connect("tcp://127.0.0.1:5557")
n_rx_samps = 0

def update(frame):
    line.set_ydata(plot_samps)
    fig.gca().relim()
    fig.gca().autoscale_view()
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


def estimateVitals():
    threading.Timer(avg_interval, estimateVitals).start()
    # DC Trend Removal
    est_samps = np.unwrap(data_samps[-num_est_samps:])
    x = np.arange(0,num_est_samps)/data_rate
    offset = np.polyfit(x, est_samps, 5)
    dcpoly = np.poly1d(offset)
    dcoffset = dcpoly(x)
    dcrem = est_samps - dcoffset
    # FFT For RR
    freq = np.fft.rfft(dcrem)
    f = np.fft.rfftfreq(num_est_samps, 1/data_rate)
    rrmax = np.argmax(freq)
    print(f[rrmax])


if __name__ == '__main__':
    thread = threading.Thread(target=zmq_handler)
    thread.daemon = True
    thread.start()

    estimateVitals()

    fig = plt.figure()
    line, = plt.plot(plot_range, plot_samps)
    animation = FuncAnimation(fig, update, interval=1000)
    plt.show()
