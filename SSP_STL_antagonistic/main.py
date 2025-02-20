from gurobipy import *
from parameter import *
from plot import *
from leader import *
from set import *
import json
import pandas
import time

time_start = time.time()

leader = LEADER(Stl_Hrizon) # build an leader model
# Get an array of random uf to calculate an input set
count = 0
while (count < sample):
    uf = generate_follower(Stl_Hrizon)
    leader.addsample(uf)
    count = count + 1

cost = leader.set()

uf_var, obj = leader.check()
uf_vec = []
for i in range(Stl_Hrizon):
    uf_vec.append([uf_var[i, 0], uf_var[i, 1]])
    # tupleditct to list transform

while (obj > 0): # indicating that this set of inputs can not resist all disturbs
    leader.addsample(uf_vec)
    cost = leader.set()  # add this disturb to intrigue a better set of inputs
    uf_var, obj = leader.check()
    uf_vec = []
    for i in range(Stl_Hrizon):
        uf_vec.append([uf_var[i, 0], uf_var[i, 1]])
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
