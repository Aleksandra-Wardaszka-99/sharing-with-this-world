import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import time
from tkinter import filedialog
import cv2
from pathlib import Path
from matplotlib import cm 
from matplotlib.animation import FuncAnimation
from matplotlib.animation import PillowWriter
import imageio.v2 as imageio 
import math

# tworzy animację i zapisuje jako gif jak zmienia się wykres surface w zależności od kąta padania wiązek -- dane i wzory są od K. Karcz 

#Ips: funcja do generowania dla danego kąta w tym szczególbym ustawieniu (patrz art. K.Karcz) wartości interferencji 

def g(X,Y, ind):
    k = (np.pi * 2 / 0.532)
    #theta =15.8 * np.pi / 180
    #theta =29.51 * np.pi / 180
    theta =ind * np.pi / 180
    sinteta = np.sin(theta)
    sintetado2 = np.power(np.sin(theta), 2)
    costeta = np.cos(theta)
    costetado2 = np.power(np.cos(theta), 2)
    print(ind)
    Ips = 4 - 2 * np.cos(2 * k * sinteta * X) \
    + 2 * np.cos(2 * k * sinteta * Y) * (sintetado2 - costetado2)\
    - 4 * costeta * np.cos(k * sinteta * (X + Y)) \
    + 4 * costeta * np.cos(k * sinteta * (X - Y))
    return Ips

#Is: funcja do generowania dla danego kąta w tym szczególbym ustawieniu (patrz art. K.Karcz) wartości interferencji 
def f(X,Y, ind):
    k = (np.pi * 2 / 0.532)
    #theta =15.8 * np.pi / 180
    #theta =29.51 * np.pi / 180
    theta =ind * np.pi / 180
    sinteta = np.sin(theta)
    sintetado2 = np.power(np.sin(theta), 2)
    costeta = np.cos(theta)
    costetado2 = np.power(np.cos(theta), 2)
    print(ind)
    Is = 4 - 2 * np.cos(2 * k * sinteta * X) - 2 * np.cos(2 * k * sinteta * Y)
    return Is

#Is: funcja do generowania dla danego kąta w tym szczególbym ustawieniu (patrz art. K.Karcz) wartości interferencji 
def e(X,Y, ind):
    k = (np.pi * 2 / 0.532)
    theta =ind * np.pi / 180
    sinteta = np.sin(theta)
    sintetado2 = np.power(np.sin(theta), 2)
    costeta = np.cos(theta)
    costetado2 = np.power(np.cos(theta), 2)
    print(ind)
    Ip = 4 - 2 * (costetado2 - sintetado2) * np.cos(2 * k * sinteta * X) \
    - 2 * (costetado2 - sintetado2) * np.cos(2 * k * sinteta * Y) \
    + 8 * sintetado2 * np.cos(k * sinteta * Y) * np.cos(k * sinteta * X)
    return Ip

# funkcja animacji, która rysuje dla poszczególnych kątów wykres przedstawiający intensywność pola interferencji dla danej polaryzacji wiązek i wyświetla wysokość ich interferecji w zależności od ustawienia 
def animate(n):
    a3.cla()
    a1.cla()
    a2.cla()
    Ips = g(X, Y, ind[n])
    Is = f(X, Y, ind[n])
    Ip = e(X, Y, ind[n])

    a1.plot_surface(X, Y, Is, cmap=cm.inferno, cstride=1, rstride=1, linewidth=0, antialiased=False)
    a2.plot_surface(X, Y, Ip, cmap=cm.inferno, cstride=1, rstride=1, linewidth=0, antialiased=False)
    a3.plot_surface(X, Y, Ips, cmap=cm.inferno, cstride=1, rstride=1, linewidth=0, antialiased=False)
    a1.set(xlabel='x', ylabel='y', zlabel = 'Interference field intensity')
    a2.set(xlabel='x', ylabel='y', zlabel = 'Interference field intensity')
    a3.set(xlabel='x', ylabel='y', zlabel = 'Interference field intensity')
    a3.set_zlim(-5, 15)
    a2.set_zlim(-5, 15)
    a1.set_zlim(-5, 15)
    a1.set_title("Is", fontsize=20)
    a2.set_title("Ip", fontsize=20)
    a3.set_title("Ips", fontsize=20)
    theta =ind[n] * np.pi / 180
    
    height = str(round(1000*np.sqrt(2)/(np.absolute(math.tan(theta)))))
    
    textA = "Wysokość:"+height+" m"
    textA = str(textA)
    print(textA)
    a1.text(0,0,45, textA, fontsize = 20)
    return fig

# ustawianie podstawowych danych dla wykresu w animacji
fig = plt.figure()
a1 = fig.add_subplot(131,projection='3d')
a2 = fig.add_subplot(132,projection='3d')
a3 = fig.add_subplot(133,projection='3d')

fig.set_figheight(12)
fig.set_figwidth(24)
x = np.linspace(0, 3, 180)
y = x
X, Y = np.meshgrid(x, y)
ind = np.linspace(2, 90, 720)
print(ind)
all_images = []

anim = FuncAnimation(
  fig = fig, func = animate, frames = len(ind), interval = 1, repeat = False
)

# jak chcesz wyświetlać, to odkomentować poniższy, ale wydłuża to czas działania app
# plt.show()
writergif = PillowWriter(fps=8)
anim.save('KK_wysokosc.gif',writer=writergif)

