import numpy as np
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d as p3
from matplotlib import animation

def playmotion():
    fig = plt.figure()
    ax = p3.Axes3D(fig)
    l, = ax.plot([0,1], [0,1], [0,1], marker='o')
    def update(i):
        l.set_data_3d(np.array([0, np.sin(i*0.1)]), np.array([0, np.cos(i*0.1)]), np.array([0, 1]))
        return [l]
    ani = animation.FuncAnimation(fig, update, frames=100, interval=20)
    plt.show()

playmotion()
