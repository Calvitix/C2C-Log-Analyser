import numpy as np
import matplotlib.pyplot as plt
import math

# Constants
S0 = 1000       # Example initial value
d_break = 10   # Distance break point
d0 = 5.0;
p = 0.4;


# Define the function
def double_decay(di):
    if di <= d_break:
        return S0 * math.pow(d0 / (d0 + di), p)
    else:
        extra_dist = di - d_break
        return S0 * math.pow(d0 / (d0 + di), p) * np.exp(-0.1 * extra_dist**1.5)

# Vectorize function to handle numpy arrays
vectorized_decay = np.vectorize(double_decay)

# Distance values
distances = np.linspace(0, 20, 500)
values = vectorized_decay(distances)

# Plot
plt.figure(figsize=(8,5))
plt.plot(distances, values, label='Double Decay Function', color='blue')
plt.xlabel('Distance')
plt.ylabel('Value')
plt.title('Example of Double Decay Function')
plt.grid(True)
plt.legend()
plt.show()
