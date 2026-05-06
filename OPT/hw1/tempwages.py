import numpy as np
from numpy.linalg import lstsq
import matplotlib.pyplot as plt

def fit_wages(t, M):
    b = np.array(M)
    A = np.column_stack((np.ones(b.shape), t))

    ret = lstsq(A, b=b, rcond=-1)
    x = ret[0]

    return x

def quarter2_2009(x):
    quarter2 = 2009.25
    return x[0] + x[1] * quarter2

def visualize_wages(params, t, M):
    n_points = 200

    start = np.min(t)
    stop = np.max(t)

    ts = np.linspace(start, stop, n_points)
    y = params[0] + params[1] * ts
    plt.plot(ts, y, 'red', label='data')
    plt.plot(t, M, 'x')

def fit_temps(t, T, omega):
    b = np.array(T)
    A = np.column_stack((
        np.ones(b.shape),
        t,
        np.sin(omega * t),
        np.cos(omega * t)
    ))

    ret = lstsq(A, b=b, rcond=-1)
    x = ret[0]

    return x

def visualize_temps(params, t, T, omega):
    n_points = 200

    start = np.min(t)
    stop = np.max(t)

    ts = np.linspace(start, stop, n_points)
    y = params[0] + params[1]*t + params[2] + np.sin(omega*t) + np.cos(omega*t)
    plt.plot(ts, y, 'red', label='data')
    plt.plot(t, T, 'x')


if __name__ == "__main__":
    data = np.loadtxt("mzdy.txt")
    data_temps = np.loadtxt("teplota.txt")
    M = np.array(data[:,1])
    t_wages = data[:,0]

    T = np.array(data_temps[:,1])
    t_temps = np.array(data_temps[:,0])

    # x = fit_wages(t, M)
    # visualize_wages(x, t, M)
    # print(x)

    x = fit_temps(t_temps, T, 1)
