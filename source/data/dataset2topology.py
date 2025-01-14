import os
import pandas as pd
import numpy as np 
import networkx as nx
import matplotlib.pyplot as plt
import math
from random import sample

node_to_index_dic = {}
index_to_node_lst = []
demand_to_index_dic = {}

def index_to_node(n):
    return(index_to_node_lst[n])

def node_to_index(node):
    return(node_to_index_dic[node])

def demand_to_index(demand):
    return(demand_to_index_dic[demand])

def process_graph(file_path):
    # Gbase = nx.MultiDiGraph()
    Gbase = nx.Graph()
    with open(file_path) as fd:
        line = fd.readline()
        camps = line.split(" ")
        net_size = int(camps[1])
        # Remove : label x y
        line = fd.readline()
        
        for i in range (net_size):
            line = fd.readline()
            node = line[0:line.find(" ")]
            node_to_index_dic[node] = i
            index_to_node_lst.append(node)
            Gbase.add_node(i)
            
        links_bw = []
        links_rtt = []
        links_name = []
        for i in range(net_size):
            links_bw.append({})
            links_rtt.append({})
            links_name.append({})
        for line in fd:
            if (not line.startswith("Link_") and not line.startswith("edge_")):
                continue
            camps = line.split(" ")
            name = str(camps[0])
            src = int(camps[1])
            dst = int(camps[2])
            weight = int(camps[3])
            bw = float(camps[4])
            links_name[src][dst] = name
            links_bw[src][dst] = bw
            links_rtt[src][dst] = weight
            Gbase.add_edge(src, dst)
    return links_name, links_bw, links_rtt, Gbase

def process_leases(links_name, links_bw, links_rtt):
    "fiber information, including src, dst, name, rtt, min_bw and max_bw"
    data = []
    for src in range(len(links_name)):
        for dst in links_name[src]:
            info = []
            info.append(links_name[src][dst]) #name 
            info.append('N' + str(src)) # source node
            info.append('N'+str(dst)) # destination node
            info.append(int(math.ceil(links_rtt[src][dst]/10000.))) # rtt length
            info.append(int(0)) # minimal bandwidth
            info.append(int(links_bw[src][dst]))
            # info.append(int(100000))
            data.append(info)
    leases_df = pd.DataFrame(data, columns=['name', 'src', 'dst', 'rtt', 'min_capacity_gbps', 'max_capacity_gbps'])
    return leases_df

def process_l3Nodes(nodes_set):
    "l3 layer nodes, including name, l1_node, stub"
    data = []
    for name in nodes_set:
        info = []
        info.append(name) #name 
        info.append(name) # l1_nodes
        info.append(False) # stub flag
        data.append(info)
    l3nodes_df = pd.DataFrame(data, columns=['name', 'l1_node', 'stub'])
    return l3nodes_df

def process_l3Links(links_name, links_bw, links_rtt):
    "ip links' information, including src, dst, name, min_capacity, final_capacity, max_capacity, fiber_name_map_spectrum and igp"
    od_pair = [] # create undirected ip links
    for src in range(len(links_name)):
        for dst in links_name[src]:
            if (dst, src) not in od_pair:
                od_pair.append((src, dst))
    data = []
    for od in od_pair:
        info = []
        info.append('ip_' + links_name[od[0]][od[1]]) #name 
        info.append('N' + str(od[0])) # source node
        info.append('N'+str(od[1])) # destination node
        info.append(int(10)) # min_capacity
        info.append(int(100)) # min_cap <= final_capacity <= max_capacity
        info.append(int(links_bw[src][dst])) # max_capacity
        # info.append(int(5000)) # max_capacity
        info.append(int(0)) #igp
        info.append(links_name[od[0]][od[1]] + ':' + str(5)) # fiber_name_map_spectrum
        data.append(info)
    iplinks_df = pd.DataFrame(data, columns=['name', 'src', 'dst', 'min_capacity_gbps', 'final_capacity_gbps', 'max_capacity_gbps', 'igp', 'fiber_name_map_spectrum'])
    return iplinks_df

def get_traffic_matrix(traffic_file):
    "Flows information, including src, dst, cos and capacity"
    # tm = np.zeros((net_size, net_size))
    tm = []
    with open(traffic_file) as fd:
        fd.readline()
        fd.readline()
        for line in fd:
            info = []
            camps = line.split(" ")
            # We force that the bws are integers
            # tm[int(camps[1]),int(camps[2])] = np.floor(float(camps[3]))
            info.append(str(camps[0])) # name
            info.append('N' + str(camps[1])) # source 
            info.append('N' + str(camps[2])) # destination
            info.append('BRONZE') # cos
            info.append(int(np.floor(float(camps[3])))) # capacity
            tm.append(info)
    # tm = sample(tm, 385)
    tm_df = pd.DataFrame(tm, columns=['name', 'src', 'dst', 'cos', 'capacity_gbps'])
    return tm_df

def load_topo_info(tm_idx):
    graph_file_path = './source/data/NEW_Janetbackbone/ALL/Janetbackbone.graph'
    # graph_file_path = './data/NEW_Janetbackbone/ALL/Janetbackbone.graph'
    # graph_file_path = './Garr199905/Garr199905.graph'
    # graph_file_path = './NEW_Janetbackbone/ALL/Janetbackbone.graph'
    links_name, links_bw, links_rtt, Graph = process_graph(graph_file_path)
    # nx.draw_networkx(Graph)
    # nx.draw(Graph, with_labels = True)
    # plt.show()
    L3_nodes_set = index_to_node_lst
    lease_df = process_leases(links_name, links_bw, links_rtt)
    # lease_df.to_excel('./source/data/Garr_syth.xlsx', sheet_name='Leases')
    l3nodes_df = process_l3Nodes(L3_nodes_set)
    # l3nodes_df.to_excel('./source/data/Garr_syth.xlsx', sheet_name='L3Nodes')
    l3links_df = process_l3Links(links_name, links_bw, links_rtt)
    # l3links_df.to_excel('./source/data/Garr_syth.xlsx', sheet_name='L3Links')

    ## traffic matrix/flows
    # tm_file_path = './source/data/Garr199905/TM/Garr199905.0.demands' #.0.demands
    tm_file_path = './source/data/NEW_Janetbackbone/ALL/TM/Janetbackbone.'
    # tm_file_path = './data/NEW_Janetbackbone/ALL/TM/Janetbackbone.'
    tm_file = tm_file_path + str(tm_idx) + '.demands'
    flows_df = get_traffic_matrix(tm_file)

    spof_list = []
    spof_df = pd.DataFrame(spof_list, columns=['fiber_names', 'cos_to_protect'])

    dataset_path = './source/data/topo_files/Topo_syth_Janetbackbone_tm_' + str(tm_idx) + '.xlsx'
    # dataset_path = './data/topo_files/Topo_syth_Janetbackbone_tm_' + str(tm_idx) + '.xlsx'

    with pd.ExcelWriter(dataset_path) as writer:
        lease_df.to_excel(writer, sheet_name='Leases')
        l3nodes_df.to_excel(writer, sheet_name='L3Nodes')
        l3links_df.to_excel(writer, sheet_name='L3Links')
        flows_df.to_excel(writer, sheet_name='Flows')
        spof_df.to_excel(writer, sheet_name='Spofs')

    return dataset_path

    # Flows_set = set()


# if __name__ == '__main__':
#     main()