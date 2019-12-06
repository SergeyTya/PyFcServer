import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation
from collections import deque
from matplotlib.ticker import FuncFormatter
from PyFcServer.server import Server


def init():  # give a clean slate to start
    line.set_ydata([np.nan] * len(x))
    return line,


def animate(i):  # update the y values (every 1000ms)
    srv.main("read_scope 0")

    # print("print ani _ ", len(srv.devices[0].scope_fifo))
    # for el in srv.devices[0].scope_fifo:
    #     scope.extend(el)
    #    srv.devices[0].scope_fifo = []

    if len(srv.devices[0].scope_fifo) > 0:
        tmp = srv.devices[0].scope_fifo.pop(0)
        for el in tmp: scope.append(el)
        line.set_ydata(scope)
    return line,


srv = Server()
srv.main("connect /dev/ttyACM0 115200 1")

max_x = 500
scope = deque([0] * max_x, maxlen=max_x)
fig, ax = plt.subplots()
max_rand = 1000
x = np.arange(0, max_x)
ax.set_ylim(-max_rand, max_rand)
line, = ax.plot(x, [0 ] *max_x)
ax.xaxis.set_major_formatter(FuncFormatter(lambda x, pos: '{:.0f}s'.format(max_x - x - 1)))
plt.xlabel('Time')
plt.ylabel('Axi')

ani = animation.FuncAnimation(
    fig, animate, init_func=init, interval=100, blit=True, save_count=10)

plt.show()
