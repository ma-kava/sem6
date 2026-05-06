import numpy as np

def f(x, y):
    return x**2 - y + np.sin(y**2 - 2*x)

# init 
x_k = np.array([1.0, 1.0])

print(f"Iteration 0: x = {x_k[0]:.6f}, y = {x_k[1]:.6f}")

for i in range(1, 10):
    x, y = x_k[0], x_k[1]
    arg = y**2 - 2*x
    
    grad = np.array([
        2*x - 2*np.cos(arg),
        2*y*np.cos(arg) - 1
    ])
    
    H = np.array([
        [2 - 4*np.sin(arg),         4*y*np.sin(arg)],
        [4*y*np.sin(arg),  2*np.cos(arg) - 4*y**2 * np.sin(arg)]
    ])
    
    step = np.linalg.solve(H, grad)
    
    x_k = x_k - step
    
    print(f"Iteration {i}: x = {x_k[0]:.6f}, y = {x_k[1]:.6f}")
    
    if np.linalg.norm(step) < 1e-6:
        print("\nSuccess!")
        break