import os, sys, json, pickle, pdb
import pandas as pd
import numpy as np 
import networkx as nx
from networkx.readwrite import json_graph
import matplotlib.pyplot as plt
import math
from random import sample
from data.dataset2topology_full import load_topo_info

from planning.ilp import ILP
from topology.topology import Topology

TM_NUM =10
BPS_NORM_FACTOR = 1000

def read_topo(tp_path, adjust_factor_in=None):
    """ load the datasets of network topology and traffic matrix from the excel
    """
    # assert(topo_name in ["A", "B", "C", "D", "E"])
    # topo_name_map_file_path = {}
    # topo_name_map_file_path["A"] = './source/data/Topo_syth.xlsx'
    
    # file_path = topo_name_map_file_path[topo_name]
    file_path = tp_path
    
    topo = Topology(adjust_factor=adjust_factor_in)
    # topo.import_fiber_from_file(file_path)
    topo.import_lease_from_file(file_path)
    topo.import_l3_node_from_file(file_path)
    topo.import_l3_link_from_file(file_path)
    topo.import_tm_from_file(file_path)
    topo.import_spof_from_file(file_path)
    
    topo.gen_failed_ip_link_and_spof_map()
    topo.generate_delta_bw_matrix_from_spof_list()

    return topo


def construct_node_features(graph, traffic_file):
    """
    construct the node features that consist of the traffic information. Specifically, each node should provide the traffic flow values of which it is the source.
    """
    df = pd.read_excel(traffic_file, sheet_name="Flows")

    tm_raw = {}
    for index, row in df.iterrows():
        try: 
            tm_raw[row['src']][row['dst']] = math.ceil(float(row['capacity_gbps']))
        except:
            tm_raw[row['src']] = {}
            tm_raw[row['src']][row['dst']] = math.ceil(float(row['capacity_gbps']))
    
    for src in tm_raw:
        attribute = []
        for dst in nx.nodes(graph):
            if dst not in tm_raw[src]:
                attribute.append(0)
            else:
                attribute.append(tm_raw[src][dst])
        graph.add_node(src, feature = attribute)

    return graph

def main():
    for tm_idx in range(TM_NUM):
        data_path = load_topo_info(tm_idx)
        adjust_factor_in = 1
        alg = "ILP"
        print(f'\n========== Fig8 start, {tm_idx}-{adjust_factor_in}, alg:{alg} ==========\n')
        ilp_solver = ILP(topo=read_topo(data_path, adjust_factor_in=adjust_factor_in))
        ilp_solver.run_ilp()
        print(f'========== Topo: A-{adjust_factor_in}, result: {ilp_solver.cost_opt} =========\n')
        
        # opt_sol = ilp_solver.opt_sol # dict
        ## load solution file
        sol_file_path = './ilp_sol.txt'
        sol_dict = json.load(open(sol_file_path))
        ## load undirected ip graph
        ip_graph = ilp_solver.graph
        # for key in opt_sol:
        #     link_idx = int(key)
        for edge in ip_graph.edges():
            ip_name = ip_graph[edge[0]][edge[1]]['name']
            ip_graph[edge[0]][edge[1]]['capacity'] = float(sol_dict[ip_name])


        ### add node features
        ip_graph = construct_node_features(ip_graph, data_path)

        ## save graph signals
        # graph_dict = nx.to_dict_of_dicts(ip_graph)
        graph_dict = json_graph.node_link_data(ip_graph)
        save_file = './source/data/signals/graph_signal_' + str(tm_idx) + '.json'
        # pdb.set_trace()
        with open(save_file, 'w') as f:
            # pickle.dump(graph_dict, f)
            f.write(json.dumps(graph_dict))
        print(f'========== Graph signal: signal_{tm_idx} has been saved! =========\n')


if __name__ == '__main__':
    main()