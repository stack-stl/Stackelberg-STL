from gurobipy import *
from parameter import *
from plot import *
from leader import *
from set import *
from initialize import *
import json
import pandas
import time

time_start = time.time()

leader = LEADER(Stl_Hrizon) # build an leader model
# Get an array of random uf to calculate an input set
count = 0
while (count < sample):
    uf2, uf3 = Set_Prob_Init(Stl_Hrizon)
    uf =[]
    for i in range(Stl_Hrizon):
        uf.append([uf2[i, 0], uf2[i, 1], uf3[i, 0], uf3[i, 1]])
    leader.addsample(uf)
    count = count + 1

cost = leader.set()

uf2_var, uf3_var, obj = leader.check(cost)
uf_vec = []
for i in range(Stl_Hrizon):
    uf_vec.append([uf2_var[i, 0], uf2_var[i, 1], uf3_var[i,0], uf3_var[i,1]])
    # tupleditct to list transform

while (obj < 0): # indicating that this set of inputs can not resist all disturbs
    leader.addsample(uf_vec)
    cost = leader.set()  # add this disturb to intrigue a better set of inputs
    uf2_var, uf3_var, obj = leader.check(cost)
    uf_vec = []
    for i in range(Stl_Hrizon):
        uf_vec.append([uf2_var[i, 0], uf2_var[i, 1], uf3_var[i,0], uf3_var[i,1]])
leader.apply()


time_end = time.time()
print("Time cost:", time_end - time_start)
print("cost is ", cost)
file_name = 'data.json'
test_dict = {
        'total': time_end - time_start,
        'cost ': cost
}
json_str = json.dumps(test_dict)
with open(file_name, 'a')as json_file:
    json_file.write(json_str)
    json_file.write('\n')

leader.print()