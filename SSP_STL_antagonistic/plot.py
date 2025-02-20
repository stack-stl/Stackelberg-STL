import matplotlib.pyplot as plt
from gurobipy import *
import matplotlib.hatch
from parameter import *
from matplotlib.patches import Rectangle
import numpy as np

def printSolution(path_sequence):
    path = []
    position_x = []
    position_y = []

    for i in range(Stl_Hrizon + 1):
        path.append([path_sequence[i][0], path_sequence[i][1]])
        position_x.append(path_sequence[i][0])
        position_y.append(path_sequence[i][1])
    path = np.array(path)

    # draw the map
    a1 = Rectangle((xA1[0], yA1[0]), xA1[1] - xA1[0], yA1[1] - yA1[0], facecolor ="blue", alpha=0.3, edgecolor= "black")
    a2 = Rectangle((xA2[0], yA2[0]), xA2[1] - xA2[0], yA2[1] - yA2[0], facecolor ="blue", alpha=0.3, edgecolor= "black")
    a3 = Rectangle((xA3[0], yA3[0]), xA3[1] - xA3[0], yA3[1] - yA3[0], facecolor ="blue", alpha=0.3, edgecolor= "black")
    ax = plt.gca()
    ax.add_patch(a1)
    ax.add_patch(a2)
    ax.add_patch(a3)

    b1 = Rectangle((xB1[0], yB1[0]), xB1[1] - xB1[0], yB1[1] - yB1[0], facecolor ="red", alpha=0.3, edgecolor= "black")
    b2 = Rectangle((xB2[0], yB2[0]), xB2[1] - xB2[0], yB2[1] - yB2[0], facecolor ="red", alpha=0.3, edgecolor= "black")
    bx = plt.gca()
    bx.add_patch(b1)
    bx.add_patch(b2)

    plt.text(9, 9, r'A1', fontsize=18, color='black')
    plt.text(2, 2, r'A2', fontsize=18, color='black')
    plt.text(9, 1, r'A3', fontsize=18, color='black')
    plt.text(2, 7.25, r'B1', fontsize=18, color='black')
    plt.text(3.5, 3.5, r'B2', fontsize=18, color='black')
    # draw the line and dots
    plt.plot(position_x, position_y, color='black', linewidth=1.3)
    plt.scatter(path[:, 0], path[:, 1], c='b')
    plt.scatter(path[0, 0], path[0, 1], c='r')
    plt.xlabel('x/m')
    plt.ylabel("y/m")
    plt.axis([0, 10, 0, 10])
    plt.grid(linestyle ="dashed", linewidth=0.5)
    
    plt.show()