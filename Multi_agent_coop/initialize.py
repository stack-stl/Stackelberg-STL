from parameter import *
from gurobipy import *


def Set_Prob_Init(len_stl):
    model_init = Model("init_problem")
    model_init.setParam('OutputFlag', 0)
    model_init.setParam("MIPFocus", 1)
    zi = model_init.addVars(len_stl + 1, 6, lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name="z_robust")
    input = model_init.addVars(len_stl, 2, lb=-u1max, ub=u1max, vtype=GRB.CONTINUOUS, name="w_robust")
    uf2 = model_init.addVars(len_stl, 2, lb=-u2max, ub=u2max, vtype=GRB.CONTINUOUS, name="w_robust")
    uf3 = model_init.addVars(len_stl, 2, lb=-u3max, ub=u3max, vtype=GRB.CONTINUOUS, name="w_robust")
    add_model_constrs_robust(model_init, input, zi, uf2, uf3, len_stl)
    obj= Add_obj_robust(model_init, zi, input, len_stl)
    model_init.optimize()
    if (model_init.status == GRB.Status.OPTIMAL):
        f2 = model_init.getAttr('x', uf2)
        f3 = model_init.getAttr('x', uf3)
        return f2, f3
        print(" it is initialized")
        print(obj.X)
    else:
        print(" ++++++++++++++++no worst feasible ui")
        sys.exit(0)


def add_model_constrs_robust(model_init, input, zi, uf2, uf3, len_stl):
    # Known system state at the current time
    model_init.addConstr((zi[0, 0] == optimal_state_sequence[0][0]), 'Known_state01')
    model_init.addConstr((zi[0, 1] == optimal_state_sequence[0][1]), 'Known_state02')
    model_init.addConstr((zi[0, 2] == optimal_state_sequence[0][2]), 'Known_state03')
    model_init.addConstr((zi[0, 3] == optimal_state_sequence[0][3]), 'Known_state04')
    model_init.addConstr((zi[0, 4] == optimal_state_sequence[0][4]), 'Known_state05')
    model_init.addConstr((zi[0, 5] == optimal_state_sequence[0][5]), 'Known_state06')
    # system model_robust
    model_init.addConstrs((zi[i + 1, 0] == zi[i, 0] + input[i, 0] for i in range(len_stl)), 'Dynamic1')
    model_init.addConstrs((zi[i + 1, 1] == zi[i, 1] + input[i, 1] for i in range(len_stl)), 'Dynamic2')
    model_init.addConstrs((zi[i + 1, 2] == zi[i, 2] + uf2[i, 0] for i in range(len_stl)), 'Dynamic3')
    model_init.addConstrs((zi[i + 1, 3] == zi[i, 3] + uf2[i, 1] for i in range(len_stl)), 'Dynamic4')
    model_init.addConstrs((zi[i + 1, 4] == zi[i, 4] + uf3[i, 0] for i in range(len_stl)), 'Dynamic5')
    model_init.addConstrs((zi[i + 1, 5] == zi[i, 5] + uf3[i, 1] for i in range(len_stl)), 'Dynamic6')
    # physical constraints - workspace
    model_init.addConstrs((xmap[0] <= zi[i, 0] for i in range(len_stl + 1)), 'Workspace1')
    model_init.addConstrs((xmap[1] >= zi[i, 0] for i in range(len_stl + 1)), 'Workspace2')
    model_init.addConstrs((ymap[0] <= zi[i, 1] for i in range(len_stl + 1)), 'Workspace3')
    model_init.addConstrs((ymap[1] >= zi[i, 1] for i in range(len_stl + 1)), 'Workspace4')
    model_init.addConstrs((xmap[0] <= zi[i, 2] for i in range(len_stl + 1)), 'Workspace1')
    model_init.addConstrs((xmap[1] >= zi[i, 2] for i in range(len_stl + 1)), 'Workspace2')
    model_init.addConstrs((ymap[0] <= zi[i, 3] for i in range(len_stl + 1)), 'Workspace3')
    model_init.addConstrs((ymap[1] >= zi[i, 3] for i in range(len_stl + 1)), 'Workspace4')
    model_init.addConstrs((xmap[0] <= zi[i, 4] for i in range(len_stl + 1)), 'Workspace1')
    model_init.addConstrs((xmap[1] >= zi[i, 4] for i in range(len_stl + 1)), 'Workspace2')
    model_init.addConstrs((ymap[0] <= zi[i, 5] for i in range(len_stl + 1)), 'Workspace3')
    model_init.addConstrs((ymap[1] >= zi[i, 5] for i in range(len_stl + 1)), 'Workspace4')
    model_init.update()

def Add_obj_robust(model_init, zi, input, len_stl):
    temp_GD = model_init.addVars(len_stl + 1, 2, lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name="temp")
    rho_GD_temp = model_init.addVars(len_stl + 1, 1, lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name="rho_GD_temp")
    rho_GD = model_init.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name="rho_GD")
    for i in range(len_stl + 1):
        model_init.addConstr((temp_GD[i, 0] == 1 - (zi[i, 2] - zi[i,0]) * (zi[i, 2] - zi[i,0]) - (zi[i, 3] - zi[i,1]) * (zi[i, 3] - zi[i,1])), "temp1")
        model_init.addConstr((temp_GD[i, 1] == 1 - (zi[i, 4] - zi[i,0]) * (zi[i, 4] - zi[i,0]) - (zi[i, 5] - zi[i,1]) * (zi[i, 5] - zi[i,1])), "temp1")
    for i in range(len_stl + 1):
        model_init.addGenConstrMin(rho_GD_temp[i, 0], [temp_GD[i, j] for j in range(2)], name="minconstr")
    model_init.addGenConstrMin(rho_GD, [rho_GD_temp[i, 0] for i in range(len_stl + 1)], name="minconstr2")
    model_init.update()

    temp_G2 = model_init.addVars(G2_t + 1, 4, lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name="temp")
    rho_G2_temp = model_init.addVars(G2_t + 1, 1, lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name="rho_G2_temp")
    rho_G2 = model_init.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name="rho_G2")
    for i in range(G2_t + 1):
        model_init.addConstr((temp_G2[i, 0] == zi[G2_tmin + i, 2] - xB2[0]), "temp1")
        model_init.addConstr((temp_G2[i, 1] == xB2[1] - zi[G2_tmin + i, 2]), "temp1")
        model_init.addConstr((temp_G2[i, 2] == zi[G2_tmin + i, 3] - yB2[0]), "temp1")
        model_init.addConstr((temp_G2[i, 3] == yB2[1] - zi[G2_tmin + i, 3]), "temp1")
    for i in range(G2_t + 1):
        model_init.addGenConstrMin(rho_G2_temp[i, 0], [temp_G2[i, j] for j in range(4)], name="minconstr")
    model_init.addGenConstrMin(rho_G2, [rho_G2_temp[i, 0] for i in range(G2_t + 1)], name="minconstr2")
    model_init.update()


    temp_F2 = model_init.addVars(F2_t + 1, 4, lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name="temp")
    rho_F2_temp = model_init.addVars(F2_t + 1, 1, lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name="rho_F2_temp")
    rho_F2 = model_init.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name="rho_F2")
    for i in range(F2_t + 1):
        model_init.addConstr((temp_F2[i, 0] == zi[F2_tmin + i, 2] - xB1[0]), "temp1")
        model_init.addConstr((temp_F2[i, 1] == xB1[1] - zi[F2_tmin + i, 2]), "temp1")
        model_init.addConstr((temp_F2[i, 2] == zi[F2_tmin + i, 3] - yB1[0]), "temp1")
        model_init.addConstr((temp_F2[i, 3] == yB1[1] - zi[F2_tmin + i, 3]), "temp1")
    for i in range(F2_t + 1):
        model_init.addGenConstrMin(rho_F2_temp[i, 0], [temp_F2[i, j] for j in range(4)], name="minconstr1")
    model_init.addGenConstrMax(rho_F2, [rho_F2_temp[i, 0] for i in range(F2_t + 1)], name="minconstr2")
    model_init.update()

    temp_F3 = model_init.addVars(F3_t + 1, 4, lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name="temp")
    rho_F3_temp = model_init.addVars(F3_t + 1, 1, lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name="rho_F3_temp")
    rho_F3 = model_init.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name="rho_F3")
    for i in range(F3_t + 1):
        model_init.addConstr((temp_F3[i, 0] == zi[F3_tmin + i, 2] - xC1[0]), "temp1")
        model_init.addConstr((temp_F3[i, 1] == xC1[1] - zi[F3_tmin + i, 2]), "temp1")
        model_init.addConstr((temp_F3[i, 2] == zi[F3_tmin + i, 3] - yC1[0]), "temp1")
        model_init.addConstr((temp_F3[i, 3] == yC1[1] - zi[F3_tmin + i, 3]), "temp1")
    for i in range(F3_t + 1):
        model_init.addGenConstrMin(rho_F3_temp[i, 0], [temp_F3[i, j] for j in range(4)], name="minconstr1")
    model_init.addGenConstrMax(rho_F3, [rho_F3_temp[i, 0] for i in range(F3_t + 1)], name="minconstr2")
    model_init.update()

    rho_F = model_init.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name="rho")

    model_init.addGenConstrMin(rho_F, [rho_F2, rho_G2, rho_F3], name="minconstr")

    temp_G1 = model_init.addVars(G1_t + 1, 4, lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name="temp")
    rho_G1_temp = model_init.addVars(G1_t + 1, 1, lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name="rho_G1_temp")
    rho_G1 = model_init.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name="rho_G1")
    for i in range(G1_t + 1):
        model_init.addConstr((temp_G1[i, 0] == zi[G1_tmin + i, 0] - xA2[0]), "temp1")
        model_init.addConstr((temp_G1[i, 1] == xA2[1] - zi[G1_tmin + i, 0]), "temp1")
        model_init.addConstr((temp_G1[i, 2] == zi[G1_tmin + i, 1] - yA2[0]), "temp1")
        model_init.addConstr((temp_G1[i, 3] == yA2[1] - zi[G1_tmin + i, 1]), "temp1")
    for i in range(G1_t + 1):
        model_init.addGenConstrMin(rho_G1_temp[i, 0], [temp_G1[i, j] for j in range(4)], name="minconstr")
    model_init.addGenConstrMin(rho_G1, [rho_G1_temp[i, 0] for i in range(G1_t + 1)], name="minconstr2")
    model_init.update()


    temp_F0 = model_init.addVars(F0_t + 1, 4, lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name="temp")
    rho_F0_temp = model_init.addVars(F0_t + 1, 1, lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name="rho_F0_temp")
    rho_F0 = model_init.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name="rho_F0")
    for i in range(F0_t + 1):
        model_init.addConstr((temp_F0[i, 0] == zi[F0_tmin + i, 0] - xA1[0]), "temp1")
        model_init.addConstr((temp_F0[i, 1] == xA1[1] - zi[F0_tmin + i, 0]), "temp1")
        model_init.addConstr((temp_F0[i, 2] == zi[F0_tmin + i, 1] - yA1[0]), "temp1")
        model_init.addConstr((temp_F0[i, 3] == yA1[1] - zi[F0_tmin + i, 1]), "temp1")
    for i in range(F0_t + 1):
        model_init.addGenConstrMin(rho_F0_temp[i, 0], [temp_F0[i, j] for j in range(4)], name="minconstr1")
    model_init.addGenConstrMax(rho_F0, [rho_F0_temp[i, 0] for i in range(F0_t + 1)], name="minconstr2")
    model_init.update()

    temp_F1 = model_init.addVars(F1_t + 1, 4, lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name="temp")
    rho_F1_temp = model_init.addVars(F1_t + 1, 1, lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name="rho_F1_temp")
    rho_F1 = model_init.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name="rho_F1")
    for i in range(F1_t + 1):
        model_init.addConstr((temp_F1[i, 0] == zi[F1_tmin + i, 0] - xA3[0]), "temp1")
        model_init.addConstr((temp_F1[i, 1] == xA3[1] - zi[F1_tmin + i, 0]), "temp1")
        model_init.addConstr((temp_F1[i, 2] == zi[F1_tmin + i, 1] - yA3[0]), "temp1")
        model_init.addConstr((temp_F1[i, 3] == yA3[1] - zi[F1_tmin + i, 1]), "temp1")
    for i in range(F1_t + 1):
        model_init.addGenConstrMin(rho_F1_temp[i, 0], [temp_F1[i, j] for j in range(4)], name="minconstr1")
    model_init.addGenConstrMax(rho_F1, [rho_F1_temp[i, 0] for i in range(F1_t + 1)], name="minconstr2")
    model_init.update()


    rho_L = model_init.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name="rho")

    model_init.addGenConstrMin(rho_L, [rho_F0, rho_F1, rho_G1], name="minconstr")

    model_init.addConstr(rho_L >= 0, "L")
    model_init.addConstr(rho_GD >= 0, "D")
    model_init.addConstr(rho_F >= 0, "D")

    obj = model_init.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name="obj")

    model_init.addConstr(obj == sum(input[j, 0] * input[j, 0] + input[j, 1] * input[j, 1] for j in range(len_stl)) / (len_stl * len_stl * 10000), "temp1")

    model_init.setObjective(obj, GRB.MINIMIZE)

    return obj
