import scipy.io as sio
import numpy as np
from math import pi
from matplotlib import pyplot as plt

def quad_to_center(d,e,f):
    x0 = -d / 2
    y0 = -e / 2
    r = np.sqrt(d**2 / 4 + e**2 / 4 - f)
    return x0, y0, r

def fit_circle_hom(X):
    x = X[:, 0]
    y = X[:, 1]
    
    A = np.column_stack((x**2 + y**2, x, y, np.ones(len(x))))
    
    _, _, Vt = np.linalg.svd(A)
    
    # solution is the smallest singular value
    p = Vt[-1, :]
    a, d, e, f = p
    
    if np.abs(a) > 1e-10:
        d = d / a
        e = e / a
        f = f / a
    
    return d, e, f

def fit_circle_nhom(X):
    x = X[:, 0]
    y = X[:, 1]
    
    A = np.column_stack((x, y, np.ones(len(x))))
    b = -(x**2 + y**2)
    
    params, _, _, _ = np.linalg.lstsq(A, b, rcond=None)
    
    d, e, f = params
    return d, e, f

def dist(X, x0, y0, r):
    distances = np.sqrt((X[:, 0] - x0)**2 + (X[:, 1] - y0)**2)
    return distances - r

def fit_circle_ransac(X, num_iter, threshold):
    best_inliers_mask = None
    max_inliers_count = 0
    num_points = X.shape[0]
    
    for i in range(num_iter):
        # pick 3 random points
        idx = np.random.choice(num_points, 3, replace=False)
        X_sample = X[idx, :]
        
        d, e, f = fit_circle_nhom(X_sample)
        # handle the case where three points lie on a straight line
        try:
            x0, y0, r = quad_to_center(d, e, f)
        except RuntimeWarning:
            continue
            
        distances = np.abs(dist(X, x0, y0, r))
        
        inliers_mask = distances < threshold
        inliers_count = np.sum(inliers_mask)
        
        if inliers_count > max_inliers_count:
            max_inliers_count = inliers_count
            best_inliers_mask = inliers_mask
            
    # take the best inliners and fit the circle for the last time
    if best_inliers_mask is not None:
        X_best_inliers = X[best_inliers_mask]
        d_best, e_best, f_best = fit_circle_nhom(X_best_inliers)
        x0_final, y0_final, r_final = quad_to_center(d_best, e_best, f_best)
        return x0_final, y0_final, r_final
    else:
        # fallback
        return 0, 0, 0

def plot_circle(x0,y0,r, color, label):
    t = np.arange(0,2*pi,0.01)
    X = x0 + r*np.cos(t)
    Y = y0 + r*np.sin(t)
    plt.plot(X,Y, color=color, label=label)


# --- MY TESTS ---

def test_dist():
    X = np.array([
        [0,0],
        [2,2],
        [0.5,0.99]
    ])

    print(dist(X, 0, 0, 1))


# --- MAIN ---

def main():
    data = sio.loadmat('data.mat')
    X = data['X'] # only inliers
    A = data['A'] # X + outliers

    def_nh = fit_circle_nhom(X)
    x0y0r_nh = quad_to_center(*def_nh)
    dnh = dist(X, *x0y0r_nh)

    def_h = fit_circle_hom(X)
    x0y0r_h = quad_to_center(*def_h)
    dh = dist(X, *x0y0r_h)

    results = {'def_nh':def_nh, 'def_h':def_h, 
               'x0y0r_nh' : x0y0r_nh, 'x0y0r_h': x0y0r_nh,
               'dnh': dnh, 'dh':dh}
    
    GT = sio.loadmat('GT.mat')
    for key in results:
        print('max difference',  np.amax(np.abs(results[key] - GT[key])), 'in', key)


    x = fit_circle_ransac(A, 2000, 0.1)

    plt.figure(1)
    plt.subplot(121)
    plt.scatter(X[:,0], X[:,1], marker='.', s=3)
    plot_circle(*x0y0r_h, 'r', 'hom')
    plot_circle(*x0y0r_nh, 'b', 'nhom')
    plt.legend()
    plt.axis('equal')    
    plt.subplot(122)
    plt.scatter(A[:,0], A[:,1], marker='.', s=2)
    plot_circle(*x, 'y', 'ransac')
    plt.legend()
    plt.axis('equal')
    plt.show()
    


if(__name__ == '__main__'):
    main()