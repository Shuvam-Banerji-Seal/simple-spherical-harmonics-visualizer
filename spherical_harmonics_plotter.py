import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.special import sph_harm
import tkinter as tk
from tkinter import Label, Entry, Button

def plot_spherical_harmonic():
    l = int(entry_l.get())
    m = int(entry_m.get())
    
    # Create grid of theta and phi values
    theta = np.linspace(0, np.pi, 100)
    phi = np.linspace(0, 2*np.pi, 100)
    theta, phi = np.meshgrid(theta, phi)
    
    # Calculate spherical harmonics
    Y_lm = sph_harm(m, l, phi, theta)
    
    # Convert spherical coordinates to Cartesian coordinates
    r = np.abs(Y_lm)
    x = r * np.sin(theta) * np.cos(phi)
    y = r * np.sin(theta) * np.sin(phi)
    z = r * np.cos(theta)
    
    # Plot the surface
    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_surface(x, y, z, cmap='viridis')

    ax.set_title(f'Spherical Harmonics Y({l}, {m})')
    ax.set_xlabel('X Axis')
    ax.set_ylabel('Y Axis')
    ax.set_zlabel('Z Axis')
    
    plt.show()

# Create a Tkinter window
root = tk.Tk()
root.title("Spherical Harmonics Plotter")

# Labels and Entry widgets for l and m
Label(root, text="l:").grid(row=0, column=0)
entry_l = Entry(root)
entry_l.grid(row=0, column=1)

Label(root, text="m:").grid(row=1, column=0)
entry_m = Entry(root)
entry_m.grid(row=1, column=1)

# Button to plot the spherical harmonic
plot_button = Button(root, text="Plot", command=plot_spherical_harmonic)
plot_button.grid(row=2, columnspan=2)

root.mainloop()
