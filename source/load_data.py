import os, sys, json, pickle
import pandas as pd
import numpy as np 
import networkx as nx
from networkx.readwrite import json_graph
import math
from random import sample

def main():
    graph_list = []
    for tm_idx in range(50):
        # data_path = load_topo_info(tm_idx)
        # adjust_factor_in = 1
        # alg = "ILP"
        # print(f'\n========== Fig8 start, {tm_idx}-{adjust_factor_in}, alg:{alg} ==========\n')
        # ilp_solver = ILP(topo=read_topo(data_path, adjust_factor_in=adjust_factor_in))
        # ilp_solver.run_ilp(delta_bw=2, ilp_solve_limit=1000, mipgap=0.1)
        # print(f'========== Topo: A-{adjust_factor_in}, result: {ilp_solver.cost_opt} =========\n')
        
        # # opt_sol = ilp_solver.opt_sol # dict
        # ## load solution file
        # sol_file_path = './ilp_sol.txt'
        # try:
        #     sol_dict = json.load(open(sol_file_path))
        #     os.system('rm ' + sol_file_path)
        # except:
        #     continue # the solution of current ilp problem is infeasible
        # ## load undirected ip graph
        # ip_graph = ilp_solver.graph
        # # for key in opt_sol:
        # #     link_idx = int(key)
        # for edge in ip_graph.edges():
        #     ip_name = ip_graph[edge[0]][edge[1]]['name']
        #     ip_graph[edge[0]][edge[1]]['capacity'] = float(sol_dict[ip_name])


        # ### add node features
        # ip_graph = construct_node_features(ip_graph, data_path)

        # ## save graph signals
        # graph_list.append(ip_graph)
        # # graph_dict = nx.to_dict_of_dicts(ip_graph)
        # graph_dict = json_graph.node_link_data(ip_graph)
        # save_file = './source/data/signals/graph_signal_' + str(tm_idx) + '.json'
        # # pdb.set_trace()
        # with open(save_file, 'w') as f:
        #     # pickle.dump(graph_dict, f)
        #     f.write(json.dumps(graph_dict))
        # print(f'========== Graph signal: signal_{tm_idx} has been saved! =========\n')

        ##============== reload the graph ====================
        save_file = './source/data/signals/graph_signal_' + str(tm_idx) + '.json'
        try: 
            with open(save_file, 'r') as f:
                # dic_graph = pickle.load(f)
                dic_graph = f.read()
            dic_graph = json.loads(dic_graph)
            # graph = nx.Graph(dic_graph)
            graph = json_graph.node_link_graph(dic_graph)
            graph_list.append(graph)
        except:
            continue
    
    # save dataset for graph signals
    file_path_t = './source/data/Claranet/raw/Claranet.pkl'
    with open(file_path_t, 'wb') as f:
            pickle.dump(obj=graph_list, file=f, protocol=pickle.HIGHEST_PROTOCOL)
    print("Saved dataset for diffusion!!")

if __name__ == '__main__':
    main()