import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d as p3
from matplotlib import animation
import numpy as np

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
l, = ax.plot([], [], [], marker='o')

def update(i):
    data = np.array([[np.sin(i*0.1), np.sin(i*0.1+1)], [np.cos(i*0.1), np.cos(i*0.1+1)]])
    l.set_data(data)
    l.set_3d_properties([i*0.01, i*0.01+0.1], 'z')
    return l,

ax.set_xlim(-1, 1)
ax.set_ylim(-1, 1)
ax.set_zlim(0, 1)

ani = animation.FuncAnimation(fig, update, frames=100, interval=20)
plt.show()
