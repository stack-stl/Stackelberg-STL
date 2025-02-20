import math

M = 1000000000

# parameters about the map
xA1 = [8, 10]
yA1 = [8, 10]  # zone A1

xA2 = [1, 4]
yA2 = [1, 4]  # zone A2

xA3 = [8, 10]
yA3 = [0, 2]  # zone A3

xB1 = [1,3]
yB1 = [6.5,8]  # zone B1

xB2 = [2, 5]
yB2 = [2, 5]  # zone B2


xmap = [0, 10]  # workspace
ymap = [0, 10]

u1max = 3
vmax = 3
u2max = 0.01

Stl_Hrizon = 25




F0_tmin = 1  # STL1: F[1,5]A1 and G[14,16]A2 and F[20,25]A3
F0_tmax = 10
F0_t = F0_tmax - F0_tmin
F1_tmin = 20
F1_tmax = 25
F1_t = F1_tmax - F1_tmin
G1_tmin = 14
G1_tmax = 16
G1_t = G1_tmax - G1_tmin

F2_tmin = 4  # STL2: F[4,9] B1 and G[13,15]B2
F2_tmax = 9
F2_t = F2_tmax - F2_tmin
G2_tmin = 12
G2_tmax = 13
G2_t = G2_tmax - G2_tmin



z0 = [2, 6, 0, 0]  # the initial states
optimal_state_sequence = [z0]
optimal_u1_sequence = []
optimal_u2_sequence = []

sample = 1
