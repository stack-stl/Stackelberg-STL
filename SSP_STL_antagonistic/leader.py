from plot import *
from set import *
from check import *


class LEADER:
    def __init__(self, len_stl):
        self.len_stl = len_stl
        self.state = optimal_state_sequence
        self.state0 = optimal_state0_sequence
        self.input = None
        self.uf_set = []

    # add a disturb set to calculate a set of input to satisfy the formuales(the disturbs are only used to find inputs)
    def addsample (self, uf):
        self.uf_set.append(uf)
    def set(self):
        if (len(self.uf_set) > 30):
            print("no inputs can satisfy all the uf")
            sys.exit(0)
        state, state0, input, obj = Set_Prob(self.uf_set, self.len_stl)

        self.input = []
        for i in range(self.len_stl):
            self.input.append([input[i, 0], input[i, 1]])

        self.state = []
        for i in range(self.len_stl + 1):
            self.state.append([state[i, 0], state[i, 1], state[i, 2], state[i, 3]])

        self.state0 = []
        for i in range(self.len_stl + 1):
            self.state0.append([state0[i, 0], state0[i, 1], state0[i, 2], state0[i, 3]])

        # print("the objective function (stl robustness + input energy) equals to", obj)
        return obj

    # check whether the input can satisfy all the disturbs and return the worst set of disturbs
    def check(self):
        uf_var, obj = Set_Prob_Robust(self.input, self.len_stl)
        # print("---------------the worst rho is ", obj,"----------------")
        return uf_var, obj


    def apply(self):
        for i in range(Stl_Hrizon):
            optimal_u1_sequence.append([self.input[i][0], self.input[i][1]])
            optimal_u2_sequence.append([self.uf_set[len(self.uf_set)-1][i][0], self.uf_set[len(self.uf_set)-1][i][1]])
            self.state[i + 1][0] = optimal_state_sequence[i][0] + 0.5 * optimal_state_sequence[i][2] + 0.125 * optimal_u1_sequence[i][0] + 0.125 * optimal_u2_sequence[i][0]
            self.state[i + 1][1] = optimal_state_sequence[i][1] + 0.5 * optimal_state_sequence[i][3] + 0.125 * optimal_u1_sequence[i][1] + 0.125 * optimal_u2_sequence[i][1]
            self.state[i + 1][2] = optimal_state_sequence[i][2] + 0.5 * optimal_u1_sequence[i][0] + 0.5 * optimal_u2_sequence[i][0]
            self.state[i + 1][3] = optimal_state_sequence[i][3] + 0.5 * optimal_u1_sequence[i][1] + 0.5 * optimal_u2_sequence[i][1]
            optimal_state_sequence.append([self.state[i + 1][0], self.state[i + 1][1], self.state[i + 1][2], self.state[i + 1][3]])
            self.state0[i + 1][0] = optimal_state0_sequence[i][0] + 0.5 * optimal_state0_sequence[i][2] + 0.125 * optimal_u1_sequence[i][0]
            self.state0[i + 1][1] = optimal_state0_sequence[i][1] + 0.5 * optimal_state0_sequence[i][3] + 0.125 * optimal_u1_sequence[i][1]
            self.state0[i + 1][2] = optimal_state0_sequence[i][2] + 0.5 * optimal_u1_sequence[i][0]
            self.state0[i + 1][3] = optimal_state0_sequence[i][3] + 0.5 * optimal_u1_sequence[i][1]
            optimal_state0_sequence.append([self.state0[i + 1][0], self.state0[i + 1][1], self.state0[i + 1][2], self.state0[i + 1][3]])
    def print(self):
        printSolution(optimal_state0_sequence)