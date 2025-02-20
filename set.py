from parameter import *
from gurobipy import *

import random


# checked
def generate_follower(length):
    uf_sequence = []
    for i in range(length):
        uf_x = u2max * 0.1 * random.randint(-10, 10)
        uf_y = u2max * 0.1 * random.randint(-10, 10)
        uf = [uf_x, uf_y]
        uf_sequence.append(uf)
    return uf_sequence


def Set_Prob(uf_set, len_stl):
    model = Model("opti_prob")
    model.setParam('OutputFlag', 0)
    len_uf_set = len(uf_set)
    # add variants
    z = model.addVars(len_uf_set * (len_stl + 1), 4, lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS,
                      name="z")  # system state
    u = model.addVars(len_stl, 2, lb=-u1max, ub=u1max, vtype=GRB.CONTINUOUS, name="u")  # control input

    add_model_constrs_with_uf(model, z, u, uf_set, len_uf_set, len_stl)
    add_stl_constrs_binary(model, z, len_uf_set, len_stl)
    obj = Add_obj(model, z, u, len_uf_set, len_stl)

    model.optimize()
    if model.status == GRB.Status.OPTIMAL:
        state = model.getAttr('x', z)
        input = model.getAttr('x', u)
        return state, input, obj.X
    else:
        print('Optimization was stopped with status ' + str(model.status))
        sys.exit(0)


def add_model_constrs_with_uf(model, z, u, uf_set, len_uf_set, len_stl):
    for j in range(len_uf_set):
        model.addConstr((z[j * (len_stl + 1), 0] == optimal_state_sequence[0][0]), 'Known_state01')
        model.addConstr((z[j * (len_stl + 1), 1] == optimal_state_sequence[0][1]), 'Known_state02')
        model.addConstr((z[j * (len_stl + 1), 2] == optimal_state_sequence[0][2]), 'Known_state03')
        model.addConstr((z[j * (len_stl + 1), 3] == optimal_state_sequence[0][3]), 'Known_state04')

    # system model
    for j in range(len_uf_set):
        model.addConstrs((z[i + 1 + j * (len_stl + 1), 0] == z[i + j * (len_stl + 1), 0] + 0.5 * z[
            i + j * (len_stl + 1), 2] + 0.125 * u[i, 0] + 0.125 * uf_set[j][i][0] for i in range(len_stl)),
                         'Dynamic_x')
        model.addConstrs((z[i + 1 + j * (len_stl + 1), 1] == z[i + j * (len_stl + 1), 1] + 0.5 * z[
            i + j * (len_stl + 1), 3] + 0.125 * u[i, 1] + 0.125 * uf_set[j][i][1] for i in range(len_stl)),
                         'Dynamic_y')
        model.addConstrs(
            (z[i + 1 + j * (len_stl + 1), 2] == z[i + j * (len_stl + 1), 2] + 0.5 * u[i, 0] + 0.5 * uf_set[j][i][0] for i
             in range(len_stl)), 'Dynamic_vx')
        model.addConstrs(
            (z[i + 1 + j * (len_stl + 1), 3] == z[i + j * (len_stl + 1), 3] + 0.5 * u[i, 1] + 0.5 * uf_set[j][i][1] for i
             in range(len_stl)), 'Dynamic_vy')
        # physical constraints - workspace
        model.addConstrs((xmap[0] <= z[i + j * (len_stl + 1), 0] for i in range(1, len_stl + 1)), 'Workspace1')
        model.addConstrs((xmap[1] >= z[i + j * (len_stl + 1), 0] for i in range(1, len_stl + 1)), 'Workspace2')
        model.addConstrs((ymap[0] <= z[i + j * (len_stl + 1), 1] for i in range(1, len_stl + 1)), 'Workspace3')
        model.addConstrs((ymap[1] >= z[i + j * (len_stl + 1), 1] for i in range(1, len_stl + 1)), 'Workspace4')
        # physical constraints - speed constraints
        model.addConstrs((-vmax <= z[i + j * (len_stl + 1), 2] for i in range(1, len_stl + 1)), 'Speed1')
        model.addConstrs((z[i + j * (len_stl + 1), 2] <= vmax for i in range(1, len_stl + 1)), 'Speed2')
        model.addConstrs((-vmax <= z[i + j * (len_stl + 1), 3] for i in range(1, len_stl + 1)), 'Speed3')
        model.addConstrs((z[i + j * (len_stl + 1), 3] <= vmax for i in range(1, len_stl + 1)), 'Speed4')
        model.update()

def add_stl_constrs_binary(model, z, len_uf_set, len_stl):

    # consider F0 and F1 formulae
    F0 = model.addVars(len_uf_set * (F0_t + 1), 1, lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name="F0C")
    F0_4 = model.addVars(len_uf_set * (F0_t + 1), 4, vtype=GRB.BINARY, name="F0_4")

    F1 = model.addVars(len_uf_set * (F1_t + 1), 1, lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name="F1C")
    F1_4 = model.addVars(len_uf_set * (F1_t + 1), 4, vtype=GRB.BINARY, name="F1_4")

    G1 = model.addVars(len_uf_set * (G1_t + 1), 1, lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name="G1C")
    G1_4 = model.addVars(len_uf_set * (G1_t + 1), 4, vtype=GRB.BINARY, name="G1_4")

    F2 = model.addVars(len_uf_set * (F2_t + 1), 1, lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name="F0C")
    F2_4 = model.addVars(len_uf_set * (F2_t + 1), 4, vtype=GRB.BINARY, name="F0_4")

    G2 = model.addVars(len_uf_set * (G2_t + 1), 1, lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name="G01")
    G2_4 = model.addVars(len_uf_set * (G2_t + 1), 4, vtype=GRB.BINARY, name="G02")

# consider F2 and G2, exist uf such that phi f is satisfied

    F2_max = model.addVars(len_uf_set, 1, lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name="F0C")

    G2_min = model.addVars(len_uf_set, 1, lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name="F0C")

    F = model.addVars(len_uf_set, 1, lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name="F0C")

    for j in range(len_uf_set):
        model.addGenConstrMax(F2_max[j, 0], [F2[i + j * (F2_t + 1), 0] for i in range(F2_t + 1)], name="maxconstr")
        model.addGenConstrMin(G2_min[j, 0], [G2[i + j * (G2_t + 1), 0] for i in range(G2_t + 1)], name="minconstr")
        model.addGenConstrMin(F[j, 0], [F2_max[j, 0], G2_min[j, 0]], name="minconstr")

    model.addConstr((sum(F[i, 0] for i in range(len_uf_set)) >= 1), 'F0')

# consider phi f implys phi l for all uf

    F0_max = model.addVars(len_uf_set, 1, lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name="F0C")

    F1_max = model.addVars(len_uf_set, 1, lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name="F0C")

    G1_min = model.addVars(len_uf_set, 1, lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name="F0C")

    L = model.addVars(len_uf_set, 1, lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name="F0C")

    FF = model.addVars(len_uf_set, 1, lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name="F0C")

    FL = model.addVars(len_uf_set, 1, lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name="F0C")

    for j in range(len_uf_set):
        model.addGenConstrMax(F0_max[j, 0], [F0[i + j * (F0_t + 1), 0] for i in range(F0_t + 1)], name="maxconstr")
        model.addGenConstrMax(F1_max[j, 0], [F1[i + j * (F1_t + 1), 0] for i in range(F1_t + 1)], name="maxconstr")
        model.addGenConstrMin(G1_min[j, 0], [G1[i + j * (G1_t + 1), 0] for i in range(G1_t + 1)], name="minconstr")
        model.addGenConstrMin(L[j, 0], [F0_max[j, 0], F1_max[j,0], G1_min[j, 0]], name="minconstr")
        model.addConstr((FF[j,0] == 1 - F[j,0]),'FF')
        model.addGenConstrMax(FL[j, 0], [FF[j, 0], L[j, 0]], name="minconstr")

    model.addConstrs((FL[i, 0] == 1 for i in range(len_uf_set)), 'FtoL')



    for j in range(len_uf_set):
        for i in range(F0_t + 1):
            model.addConstrs((F0[i + j * (F0_t + 1), 0] <= F0_4[i + j * (F0_t + 1), p] for p in range(4)), 'F2')
            model.addConstr((sum(F0_4[i + j * (F0_t + 1), p] for p in range(4)) - 3 <= F0[i + j * (F0_t + 1), 0]), 'F3')
        model.addConstrs((z[j * (len_stl + 1) + F0_tmin + i, 0] - xA1[0] <= M * F0_4[i + j * (F0_t + 1), 0] for i in range(F0_t + 1)), 'F4')
        model.addConstrs((-z[j * (len_stl + 1) + F0_tmin + i, 0] + xA1[0] <= M * (1 - F0_4[i + j * (F0_t + 1), 0]) for i in range(F0_t + 1)), 'F5')
        model.addConstrs((-z[j * (len_stl + 1) + F0_tmin + i, 0] + xA1[1] <= M * F0_4[i + j * (F0_t + 1), 1] for i in range(F0_t + 1)), 'F6')
        model.addConstrs((z[j * (len_stl + 1) + F0_tmin + i, 0] - xA1[1] <= M * (1 - F0_4[i + j * (F0_t + 1), 1]) for i in range(F0_t + 1)), 'F7')
        model.addConstrs((z[j * (len_stl + 1) + F0_tmin + i, 1] - yA1[0] <= M * F0_4[i + j * (F0_t + 1), 2] for i in range(F0_t + 1)), 'F8')
        model.addConstrs((-z[j * (len_stl + 1) + F0_tmin + i, 1] + yA1[0] <= M * (1 - F0_4[i + j * (F0_t + 1), 2]) for i in range(F0_t + 1)), 'F9')
        model.addConstrs((-z[j * (len_stl + 1) + F0_tmin + i, 1] + yA1[1] <= M * F0_4[i + j * (F0_t + 1), 3] for i in range(F0_t + 1)), 'F00')
        model.addConstrs((z[j * (len_stl + 1) + F0_tmin + i, 1] - yA1[1] <= M * (1 - F0_4[i + j * (F0_t + 1), 3]) for i in range(F0_t + 1)), 'F01')
        for i in range(F1_t + 1):
            model.addConstrs((F1[i + j * (F1_t + 1), 0] <= F1_4[i + j * (F1_t + 1), p] for p in range(4)), 'F2')
            model.addConstr((sum(F1_4[i + j * (F1_t + 1), p] for p in range(4)) - 3 <= F1[i + j * (F1_t + 1), 0]), 'F3')
        model.addConstrs((z[j * (len_stl + 1) + F1_tmin + i, 0] - xA3[0] <= M * F1_4[i + j * (F1_t + 1), 0] for i in range(F1_t + 1)), 'F4')
        model.addConstrs((-z[j * (len_stl + 1) + F1_tmin + i, 0] + xA3[0] <= M * (1 - F1_4[i + j * (F1_t + 1), 0]) for i in range(F1_t + 1)), 'F5')
        model.addConstrs((-z[j * (len_stl + 1) + F1_tmin + i, 0] + xA3[1] <= M * F1_4[i + j * (F1_t + 1), 1] for i in range(F1_t + 1)), 'F6')
        model.addConstrs((z[j * (len_stl + 1) + F1_tmin + i, 0] - xA3[1] <= M * (1 - F1_4[i + j * (F1_t + 1), 1]) for i in range(F1_t + 1)), 'F7')
        model.addConstrs((z[j * (len_stl + 1) + F1_tmin + i, 1] - yA3[0] <= M * F1_4[i + j * (F1_t + 1), 2] for i in range(F1_t + 1)), 'F8')
        model.addConstrs((-z[j * (len_stl + 1) + F1_tmin + i, 1] + yA3[0] <= M * (1 - F1_4[i + j * (F1_t + 1), 2]) for i in range(F1_t + 1)), 'F9')
        model.addConstrs((-z[j * (len_stl + 1) + F1_tmin + i, 1] + yA3[1] <= M * F1_4[i + j * (F1_t + 1), 3] for i in range(F1_t + 1)), 'F00')
        model.addConstrs((z[j * (len_stl + 1) + F1_tmin + i, 1] - yA3[1] <= M * (1 - F1_4[i + j * (F1_t + 1), 3]) for i in range(F1_t + 1)), 'F01')
        for i in range(F2_t + 1):
            model.addConstrs((F2[i + j * (F2_t + 1), 0] <= F2_4[i + j * (F2_t + 1), p] for p in range(4)), 'F2')
            model.addConstr((sum(F2_4[i + j * (F2_t + 1), p] for p in range(4)) - 3 <= F2[i + j * (F2_t + 1), 0]), 'F3')
        model.addConstrs((z[j * (len_stl + 1) + F2_tmin + i, 0] - xB1[0] <= M * F2_4[i + j * (F2_t + 1), 0] for i in range(F2_t + 1)), 'F4')
        model.addConstrs((-z[j * (len_stl + 1) + F2_tmin + i, 0] + xB1[0] <= M * (1 - F2_4[i + j * (F2_t + 1), 0]) for i in range(F2_t + 1)), 'F5')
        model.addConstrs((-z[j * (len_stl + 1) + F2_tmin + i, 0] + xB1[1] <= M * F2_4[i + j * (F2_t + 1), 1] for i in range(F2_t + 1)), 'F6')
        model.addConstrs((z[j * (len_stl + 1) + F2_tmin + i, 0] - xB1[1] <= M * (1 - F2_4[i + j * (F2_t + 1), 1]) for i in range(F2_t + 1)), 'F7')
        model.addConstrs((z[j * (len_stl + 1) + F2_tmin + i, 1] - yB1[0] <= M * F2_4[i + j * (F2_t + 1), 2] for i in range(F2_t + 1)), 'F8')
        model.addConstrs((-z[j * (len_stl + 1) + F2_tmin + i, 1] + yB1[0] <= M * (1 - F2_4[i + j * (F2_t + 1), 2]) for i in range(F2_t + 1)), 'F9')
        model.addConstrs((-z[j * (len_stl + 1) + F2_tmin + i, 1] + yB1[1] <= M * F2_4[i + j * (F2_t + 1), 3] for i in range(F2_t + 1)), 'F00')
        model.addConstrs((z[j * (len_stl + 1) + F2_tmin + i, 1] - yB1[1] <= M * (1 - F2_4[i + j * (F2_t + 1), 3]) for i in range(F2_t + 1)), 'F01')
        for i in range(G1_t + 1):
            model.addConstrs((G1[i + j * (G1_t + 1), 0] <= G1_4[i + j * (G1_t + 1), p] for p in range(4)), 'G04')
            model.addConstr((sum(G1_4[i + j * (G1_t + 1), p] for p in range(4)) - 3 <= G1[i + j * (G1_t + 1), 0]), 'G05')
        model.addConstrs((z[j * (len_stl + 1) + G1_tmin + i, 0] - xA2[0] <= M * G1_4[i + j * (G1_t + 1), 0] for i in range(G1_t + 1)), 'G06')
        model.addConstrs((-z[j * (len_stl + 1) + G1_tmin + i, 0] + xA2[0] <= M * (1 - G1_4[i + j * (G1_t + 1), 0]) for i in range(G1_t + 1)), 'G07')
        model.addConstrs((-z[j * (len_stl + 1) + G1_tmin + i, 0] + xA2[1] <= M * G1_4[i + j * (G1_t + 1), 1] for i in range(G1_t + 1)), 'G08')
        model.addConstrs((z[j * (len_stl + 1) + G1_tmin + i, 0] - xA2[1] <= M * (1 - G1_4[i + j * (G1_t + 1), 1]) for i in range(G1_t + 1)), 'G09')
        model.addConstrs((z[j * (len_stl + 1) + G1_tmin + i, 1] - yA2[0] <= M * G1_4[i + j * (G1_t + 1), 2] for i in range(G1_t + 1)), 'G010')
        model.addConstrs((-z[j * (len_stl + 1) + G1_tmin + i, 1] + yA2[0] <= M * (1 - G1_4[i + j * (G1_t + 1), 2]) for i in range(G1_t + 1)), 'G011')
        model.addConstrs((-z[j * (len_stl + 1) + G1_tmin + i, 1] + yA2[1] <= M * G1_4[i + j * (G1_t + 1), 3] for i in range(G1_t + 1)), 'G012')
        model.addConstrs((z[j * (len_stl + 1) + G1_tmin + i, 1] - yA2[1] <= M * (1 - G1_4[i + j * (G1_t + 1), 3]) for i in range(G1_t + 1)), 'G013')
        for i in range(G2_t + 1):
            model.addConstrs((G2[i + j * (G2_t + 1), 0] <= G2_4[i + j * (G2_t + 1), p] for p in range(4)), 'G04')
            model.addConstr((sum(G2_4[i + j * (G2_t + 1), p] for p in range(4)) - 3 <= G2[i + j * (G2_t + 1), 0]), 'G05')
        model.addConstrs((z[j * (len_stl + 1) + G2_tmin + i, 0] - xB2[0] <= M * G2_4[i + j * (G2_t + 1), 0] for i in range(G2_t + 1)), 'G06')
        model.addConstrs((-z[j * (len_stl + 1) + G2_tmin + i, 0] + xB2[0] <= M * (1 - G2_4[i + j * (G2_t + 1), 0]) for i in range(G2_t + 1)), 'G07')
        model.addConstrs((-z[j * (len_stl + 1) + G2_tmin + i, 0] + xB2[1] <= M * G2_4[i + j * (G2_t + 1), 1] for i in range(G2_t + 1)), 'G08')
        model.addConstrs((z[j * (len_stl + 1) + G2_tmin + i, 0] - xB2[1] <= M * (1 - G2_4[i + j * (G2_t + 1), 1]) for i in range(G2_t + 1)), 'G09')
        model.addConstrs((z[j * (len_stl + 1) + G2_tmin + i, 1] - yB2[0] <= M * G2_4[i + j * (G2_t + 1), 2] for i in range(G2_t + 1)), 'G010')
        model.addConstrs((-z[j * (len_stl + 1) + G2_tmin + i, 1] + yB2[0] <= M * (1 - G2_4[i + j * (G2_t + 1), 2]) for i in range(G2_t + 1)), 'G011')
        model.addConstrs((-z[j * (len_stl + 1) + G2_tmin + i, 1] + yB2[1] <= M * G2_4[i + j * (G2_t + 1), 3] for i in range(G2_t + 1)), 'G012')
        model.addConstrs((z[j * (len_stl + 1) + G2_tmin + i, 1] - yB2[1] <= M * (1 - G2_4[i + j * (G2_t + 1), 3]) for i in range(G2_t + 1)), 'G013')


def Add_obj(model, z, u, len_uf_set, len_stl):
    temp_G1 = model.addVars((G1_t + 1) * len_uf_set, 4, lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name="temp")
    rho_G1_temp = model.addVars((G1_t + 1) * len_uf_set, 1, lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name="rho_G1_temp")
    rho_G1 = model.addVars(len_uf_set, 1, lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name="rho_G1")
    for j in range(len_uf_set):
        for i in range(G1_t + 1):
            model.addConstr((temp_G1[i + j * (G1_t + 1), 0] == z[G1_tmin + i + j * (len_stl + 1), 0] - xA2[0]), "temp1")
            model.addConstr((temp_G1[i + j * (G1_t + 1), 1] == xA2[1] - z[G1_tmin + i + j * (len_stl + 1), 0]), "temp1")
            model.addConstr((temp_G1[i + j * (G1_t + 1), 2] == z[G1_tmin + i + j * (len_stl + 1), 1] - yA2[0]), "temp1")
            model.addConstr((temp_G1[i + j * (G1_t + 1), 3] == yA2[1] - z[G1_tmin + i + j * (len_stl + 1), 1]), "temp1")
            model.addGenConstrMin(rho_G1_temp[i + j * (G1_t + 1), 0], [temp_G1[i + j * (G1_t + 1), p] for p in range(4)], name="minconstr")
        model.addGenConstrMin(rho_G1[j, 0], [rho_G1_temp[i + j * (G1_t + 1), 0] for i in range(G1_t + 1)], name="minconstr")

    temp_F0 = model.addVars((F0_t + 1) * len_uf_set, 4, lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name="temp")
    rho_F0_temp = model.addVars((F0_t + 1) * len_uf_set, 1, lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name="rho_F0_temp")
    rho_F0 = model.addVars(len_uf_set, 1, lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name="rho_F0")
    for j in range(len_uf_set):
        for i in range(F0_t + 1):
            model.addConstr((temp_F0[i + j * (F0_t + 1), 0] == z[F0_tmin + i + j * (len_stl + 1), 0] - xA1[0]), "temp1")
            model.addConstr((temp_F0[i + j * (F0_t + 1), 1] == xA1[1] - z[F0_tmin + i + j * (len_stl + 1), 0]), "temp1")
            model.addConstr((temp_F0[i + j * (F0_t + 1), 2] == z[F0_tmin + i + j * (len_stl + 1), 1] - yA1[0]), "temp1")
            model.addConstr((temp_F0[i + j * (F0_t + 1), 3] == yA1[1] - z[F0_tmin + i + j * (len_stl + 1), 1]), "temp1")
            model.addGenConstrMin(rho_F0_temp[i + j * (F0_t + 1), 0], [temp_F0[i + j * (F0_t + 1), p] for p in range(4)], name="minconstr")
        model.addGenConstrMax(rho_F0[j, 0], [rho_F0_temp[i + j * (F0_t + 1), 0] for i in range(F0_t + 1)], name="maxconstr")

    temp_F1 = model.addVars((F1_t + 1) * len_uf_set, 4, lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name="temp")
    rho_F1_temp = model.addVars((F1_t + 1) * len_uf_set, 1, lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name="rho_F1_temp")
    rho_F1 = model.addVars(len_uf_set, 1, lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name="rho_F1")
    for j in range(len_uf_set):
        for i in range(F1_t + 1):
            model.addConstr((temp_F1[i + j * (F1_t + 1), 0] == z[F1_tmin + i + j * (len_stl + 1), 0] - xA3[0]), "temp1")
            model.addConstr((temp_F1[i + j * (F1_t + 1), 1] == xA3[1] - z[F1_tmin + i + j * (len_stl + 1), 0]), "temp1")
            model.addConstr((temp_F1[i + j * (F1_t + 1), 2] == z[F1_tmin + i + j * (len_stl + 1), 1] - yA3[0]), "temp1")
            model.addConstr((temp_F1[i + j * (F1_t + 1), 3] == yA3[1] - z[F1_tmin + i + j * (len_stl + 1), 1]), "temp1")
            model.addGenConstrMin(rho_F1_temp[i + j * (F1_t + 1), 0], [temp_F1[i + j * (F1_t + 1), p] for p in range(4)], name="minconstr")
        model.addGenConstrMax(rho_F1[j, 0], [rho_F1_temp[i + j * (F1_t + 1), 0] for i in range(F1_t + 1)], name="maxconstr")

    rho = model.addVars(len_uf_set, 1, lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name="rho")

    for i in range(len_uf_set):
        model.addGenConstrMin(rho[i, 0], [rho_F0[i, 0], rho_G1[i, 0], rho_F1[i, 0]], name="minconstr")

    k = model.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name="rho")

    model.addGenConstrMin(k, [rho[i, 0] for i in range(len_uf_set)], name="minconstr")


    # objective function
    obj = model.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name="temp")
    model.addConstr(obj == sum(u[j, 0] * u[j, 0] + u[j, 1] * u[j, 1] for j in range(len_stl)) / (len_stl * len_stl * 10000) - k, "temp1")
    model.setObjective(obj, GRB.MINIMIZE)
    return obj



